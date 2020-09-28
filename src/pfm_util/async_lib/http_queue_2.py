import asyncio
import logging
from string import Template
from time import perf_counter_ns
from typing import (
    Any,
    ByteString,
    Dict,
    Iterable,
    List,
    Optional,
    Sequence,
    Type,
    Union,
)

import aiohttp

logger = logging.getLogger(__name__)
# logger.addHandler(logging.NullHandler())
HTTP_STATUS_CODES_TO_RETRY = [500, 502, 503, 504]
# TODO need to trace logic through http requests, think about flow, error flags.
# TODO helper classes to make it easier, get, post, json response, etc
# TODO testing, examine logs for logic and sense.
# TODO more exception conditions that trigger retry?


class FailedRequest(Exception):
    """
    A wrapper of all possible exception during a HTTP request
    """

    def __init__(self, *, raised="", message="", code="", url=""):
        self.raised = raised
        self.message = message
        self.code = code
        self.url = url

        super().__init__(
            "code:{c} url={u} message={m} raised={r}".format(
                c=self.code, u=self.url, m=self.message, r=self.raised
            )
        )


class FailedRequestWithRetry(FailedRequest):
    def __init__(self, *, raised="", message="", code="", url=""):
        super().__init__(raised=raised, message=message, code=code, url=url)


class FailedRequestNoRetry(FailedRequest):
    def __init__(self, *, raised="", message="", code="", url=""):
        super().__init__(raised=raised, message=message, code=code, url=url)


class RequestRetry(Exception):
    def __init__(self, *, foo=None, **kwargs):
        super().__init__()


async def http_worker(queue, session):
    while True:
        action = await queue.get()
        start = perf_counter_ns()
        await action.do_action(queue=queue, session=session)
        http_end = perf_counter_ns()
        await action.handle_results(queue=queue)
        handle_results_end = perf_counter_ns()
        queue.task_done()


def default_object_check(init_attribute, default_constructor):
    # TODO save to utilities
    if init_attribute is None:
        return default_constructor()
    return init_attribute


def run_actions(actions, workers: int):
    runner = HttpQueueRunner()
    asyncio.run(runner.do_queue(actions, workers))


class HttpQueueRunner:
    def __init__(self, worker=None):
        if worker is None:
            self.worker = http_worker
        else:
            self.worker = worker
        self.queue = None

    async def do_queue(self, actions: Sequence[Type["HttpAction"]], workers: int):
        logger.info(
            "Starting %s queue with %s workers", self.__class__.__name__, workers
        )
        start = perf_counter_ns()
        async with aiohttp.ClientSession() as session:
            self.queue = asyncio.Queue()
            task_workers = []
            for _ in range(workers):
                task = asyncio.create_task(self.worker(self.queue, session))
                task_workers.append(task)
            logger.info("Adding %d actions to queue", len(actions))
            for action in actions:
                self.queue.put_nowait(action)
            await self.queue.join()
            for task in task_workers:
                task.cancel()
            await asyncio.gather(*task_workers, return_exceptions=True)
        end = perf_counter_ns()
        logger.info(
            "Queue completed -  took %s seconds", f"{(end-start)/1000000000:9f}"
        )


class HttpActionText:
    """
    [summary]
    """

    def __init__(
        self,
        name: str,
        method: str,
        url_template: str,
        url_params: dict = None,
        retry_limit: int = 5,
        read_timeout: int = 15,
        backoff_interval: float = 0.9,
        result_handlers: List = None,
        context: dict = None,
        parent_action=None,
        child_actions=None,
        response_encoding=None,
        **kwargs,
    ):
        self.name: str = name
        self.context = default_object_check(context, dict)
        self.result_handlers = default_object_check(result_handlers, list)
        self.method = method
        self.retry_limit = retry_limit
        self.read_timeout = read_timeout
        self.backoff_interval = backoff_interval
        self.attempt = 0
        self.url_params = default_object_check(url_params, dict)
        self.child_actions = default_object_check(child_actions, list)
        self.parent_action = parent_action
        self.url_template = url_template
        self.url = Template(url_template).substitute(self.url_params)
        self.response: Optional[aiohttp.ClientResponse] = None
        self.response_data: Union[None, str, bytes] = None
        self.response_encoding = response_encoding
        self.kwargs = kwargs
        if method not in ["get", "patch", "post"]:
            raise ValueError

    def __repr__(self):
        fields = self.__dict__.keys()
        field_strings = []
        for field in fields:
            stub = f"{field}: {self.__dict__[field]!r}"
            field_strings.append(stub)
        repr_string = f"{self.__class__.__name__}({', '.join(field_strings)})"
        return repr_string

    async def handle_results(self, queue):
        for handler in self.result_handlers:
            await handler.handle_result(self, queue, self.response)

    async def do_action(self, queue, session: aiohttp.ClientSession):
        logger.debug("Doing action: %s", self.name)
        if self.retry_limit == -1:  # -1 means retry indefinitely
            self.attempt = -1
        elif self.retry_limit == 0:  # Zero means don't retry
            self.attempt = 1
        else:  # any other value means retry N times
            self.attempt = self.retry_limit + 1

        interval = self.backoff_interval
        raised_exc: Optional[Type[Exception]] = None
        while self.attempt != 0:
            if raised_exc:
                logger.error(
                    'caught "%s" url:%s method:%s, remaining tries %s, '
                    "sleeping %.2fsecs",
                    raised_exc,
                    self.method.upper(),
                    self.url,
                    self.attempt,
                    interval,
                )
                await asyncio.sleep(interval)
                # bump interval for the next possible attempt
                interval = interval * self.backoff_interval
            logger.info(
                "sending %s %s with %s", self.method.upper(), self.url, self.kwargs
            )
            try:
                timeout = aiohttp.ClientTimeout(total=self.read_timeout)

                async with session.request(
                    self.method, self.url, timeout=timeout, **self.kwargs
                ) as response:
                    self.response = response
                    response.raise_for_status()
                    if response.status == 200:
                        # A successful response that should have data
                        self.response_data = await response.text(self.response_encoding)
                        logger.info(
                            "code:%s url:%s method:%s reason:%s",
                            response.status,
                            self.url,
                            self.method.upper(),
                            response.reason,
                        )
                    else:
                        logger.warning(
                            "Unhandled successful return for action:%s", self
                        )
                        # 200 < status < 400
                        raise NotImplementedError()

            except aiohttp.ClientResponseError as exc:
                if exc.status in HTTP_STATUS_CODES_TO_RETRY:
                    # retry
                    raised_exc = exc
                    continue
                else:
                    logger.warning(
                        "Request failed no retry. code:%s reason:%s Action:%s url:%s",
                        exc.status,
                        exc.message,
                        self.name,
                        self.url,
                    )
                    break

            except (
                FailedRequestNoRetry,
                # aiohttp.ClientRequestError,
                aiohttp.ClientOSError,
            ) as exc:
                logger.warning(
                    "Request failed no retry. Exception:%s code:%s reason:%s Action:%s url:%s",
                    exc,
                    self.response.status or "None",
                    self.response.message or "None",
                    self.name,
                    self.url,
                )
                return

            except (
                FailedRequestWithRetry,
                aiohttp.ServerDisconnectedError,
                aiohttp.ServerTimeoutError,
                asyncio.TimeoutError,
            ) as exc:
                raised_exc = exc
                continue
            else:
                # No errors, action complete
                raised_exc = None
                return

            self.attempt -= 1

        # if raised_exc is not None:
        #     raise raised_exc
        #
        ##
        #

        # try:
        #     async with session.request(
        #         self.method,
        #         self.url,
        #         params=self.request_parameters,
        #         json=self.json_parameters,
        #         **self.request_config_parameters,
        #     ) as response:
        #         await self.handle_results(queue, response)

        # except Exception:
        #     # TODO better error recovery, for instance aiohttp.client_exceptions.ServerDisconnectedError
        #     logger.exception("Exception in do_action for %s", self.name)
