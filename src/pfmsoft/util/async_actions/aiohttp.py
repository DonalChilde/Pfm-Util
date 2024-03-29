import logging
from asyncio import Task, create_task, gather
from asyncio.queues import Queue
from string import Template
from time import perf_counter_ns
from typing import TYPE_CHECKING, Any, Dict, Optional, Sequence, Union

from aiohttp import ClientResponse, ClientSession

from pfmsoft.util.collection.misc import optional_object

logger = logging.getLogger(__name__)


HTTP_STATUS_CODES_TO_RETRY = [500, 502, 503, 504]


class AiohttpQueueWorker:
    def __init__(self) -> None:
        pass

    def get_worker(self, queue: Queue, session: ClientSession):
        async def consumer(queue):
            while True:
                action: AiohttpAction = await queue.get()
                try:
                    await action.do_action(queue, session)
                except Exception as ex:
                    print(ex)
                queue.task_done()

        worker = consumer(queue)
        return worker


class AiohttpAction:
    """
    A self contained unit of execution

    [extended_summary]

    :param AsyncAction: [description]
    :type AsyncAction: [type]
    """

    def __init__(
        self,
        method: str,
        url_template: str,
        url_parameters: Optional[dict] = None,
        retry_limit: int = 0,
        context: Optional[dict] = None,
        request_kwargs: Optional[dict] = None,
        name: str = "",
        id_=None,
        action_callbacks: Optional[Dict[str, Sequence["AiohttpActionCallback"]]] = None,
        action_messengers: Optional[Sequence["AiohttpActionMessenger"]] = None,
    ) -> None:
        self.name = name
        self.id_ = id_
        self.action_callbacks = action_callbacks
        self.action_messengers = action_messengers
        self.method = method
        self.url_template = url_template
        self.url_parameters: Dict = optional_object(url_parameters, dict)
        self.url = Template(url_template).substitute(self.url_parameters)
        self.retry_limit = retry_limit
        self.response: Optional[ClientResponse] = None
        # self.response_data: Optional[Union[str, dict, bytes]] = None
        self.retry_count: int = 0
        self.result: Any = None
        self.request_kwargs = optional_object(request_kwargs, dict)
        self.context = optional_object(context, dict)
        # self.json_data = None

    async def success(self, **kwargs):
        success_callbacks = self.action_callbacks.get("success", [])
        for callback in success_callbacks:
            await callback.do_callback(caller=self, **kwargs)

    async def fail(self, **kwargs):
        fail_callbacks = self.action_callbacks.get("fail", [])
        for callback in fail_callbacks:
            await callback.do_callback(caller=self, **kwargs)

    async def retry(self, **kwargs):
        retry_callbacks = self.action_callbacks.get("retry", [])
        for callback in retry_callbacks:
            await callback.do_callback(caller=self, **kwargs)

    async def send_message(self, message, **kwargs):
        messengers = self.action_messengers or []
        for messenger in messengers:
            messenger.action_message(message=message, **kwargs)

    async def do_action(self, queue: Queue, session: ClientSession, *args, **kwargs):
        try:
            if self.retry_count <= self.retry_limit:
                async with session.request(
                    self.method, self.url, **self.request_kwargs
                ) as response:
                    self.response = response
                    await self.check_response(queue)
            else:
                await self.fail()
        except Exception as e:
            print(e)

    async def check_response(self, queue: Queue):
        if self.response is not None:
            if self.response.status == 200:
                await self.success()
            elif self.response.status in HTTP_STATUS_CODES_TO_RETRY:
                self.retry_count += 1
                await queue.put(self)
                await self.retry()
            else:
                await self.fail()
        else:
            logger.warning(
                "Checked response before response recieved. This should not be possible."
            )


async def do_aiohttp_action_queue(
    actions: Sequence[AiohttpAction],
    worker_factories: Sequence[AiohttpQueueWorker],
    session_kwargs=None,
):
    start = perf_counter_ns()
    if session_kwargs is None:
        session_kwargs = {}
    queue: Queue = Queue()
    async with ClientSession(**session_kwargs) as session:
        logger.info(
            "Starting queue with %s workers and %s actions",
            len(worker_factories),
            len(actions),
        )

        worker_tasks = []
        for factory in worker_factories:
            worker_task: Task = create_task(factory.get_worker(queue, session))
            worker_tasks.append(worker_task)
        logger.info("Adding %d actions to queue", len(actions))
        for action in actions:
            queue.put_nowait(action)
        await queue.join()
        for worker_task in worker_tasks:
            worker_task.cancel()
        await gather(*worker_tasks, return_exceptions=True)
        end = perf_counter_ns()
        # TODO change timing formatter to lib method
        seconds = (end - start) / 1000000000
        logger.info(
            "Queue completed -  took %s seconds, %s actions per second.",
            f"{seconds:9f}",
            f"{len(actions)/seconds:1f}",
        )


class AiohttpActionCallback:
    def __init__(self, *args, **kwargs) -> None:
        pass

    async def do_callback(self, caller: AiohttpAction, *args, **kwargs):
        pass


class AiohttpActionMessenger:
    def __init__(self) -> None:
        pass

    async def action_message(self, message, *args, **kwargs):
        pass


class ResponseToJson(AiohttpActionCallback):
    def __init__(self) -> None:
        super().__init__()

    async def do_callback(self, caller: AiohttpAction, *args, **kwargs):
        if caller.response is not None:
            caller.result = await caller.response.json()


class ResponseToText(AiohttpActionCallback):
    def __init__(self) -> None:
        super().__init__()

    async def do_callback(self, caller: AiohttpAction, *args, **kwargs):
        if caller.response is not None:
            caller.result = await caller.response.text()


class LogSuccess(AiohttpActionCallback):
    def __init__(self) -> None:
        super().__init__()

    async def do_callback(self, caller: AiohttpAction, *args, **kwargs):
        logger.info(
            "Request method: %s to url: %s succeeded.", caller.method, caller.url
        )


class LogFail(AiohttpActionCallback):
    def __init__(self) -> None:
        super().__init__()

    async def do_callback(self, caller: AiohttpAction, *args, **kwargs):
        logger.warning(
            "Request method: %s to url: %s failed.", caller.method, caller.url
        )


class LogRetry(AiohttpActionCallback):
    def __init__(self) -> None:
        super().__init__()

    async def do_callback(self, caller: AiohttpAction, *args, **kwargs):
        # TODO more informative messages. Remaining retries.
        logger.info(
            "Request method: %s to url: %s submitted for retry.",
            caller.method,
            caller.url,
        )


class CheckForPages(AiohttpActionCallback):
    def __init__(self) -> None:
        super().__init__()

    async def do_callback(self, caller: AiohttpAction, *args, **kwargs):
        """
        - check for pages
        - copy action, with new page request
        - add to list of child actions? use context variable?
        - add action to queue

        [extended_summary]

        :param caller: [description]
        :type caller: AiohttpAction
        """
