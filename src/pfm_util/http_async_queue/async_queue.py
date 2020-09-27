"""
[summary]

Returns
-------
[type]
    [description]

    TODO Track retries and total actions, log actions per second. subclass Queue?
"""

import asyncio
import copy
import csv
import json
import logging
import random
from abc import ABC, abstractmethod
from pathlib import Path
from string import Template
from time import perf_counter_ns
from typing import Any, Dict, Iterable, List, Optional, Sequence, Type

import aiohttp

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


async def basic_worker(queue):
    while True:
        action = await queue.get()
        await action.do_action(queue=queue)
        await action.handle_results(queue=queue)
        queue.task_done()


class QueueActionABC(ABC):
    def __init__(self, name, result_handlers=None, context=None):
        self.name: str = name
        if not context:
            self.context = {}
        else:
            self.context = context
        if not result_handlers:
            self.result_handlers = []
        else:
            self.result_handlers = result_handlers

    @abstractmethod
    async def do_action(self, queue, *args, **kwargs):
        pass

    async def handle_results(self, queue, *args, **kwargs):
        for handler in self.result_handlers:
            await handler.handle_result(self, queue)


class ResultHandlerABC(ABC):
    def __init__(self):
        pass

    @abstractmethod
    async def handle_result(self, action, queue, *args, **kwargs):
        pass


class ExampleAction(QueueActionABC):
    def __init__(self, name, result_handlers=None, context=None):
        super().__init__(name, result_handlers=result_handlers, context=context)
        self.sleep_for = 0

    async def do_action(self, queue, *args, **kwargs):
        _ = queue
        self.sleep_for = random.uniform(0.05, 1.0)
        await asyncio.sleep(self.sleep_for)
        # self.context["result"] = f"{self.name} Action Completed. Slept for {sleep_for}"


class ExampleHandler(ResultHandlerABC):
    def __init__(self):
        super().__init__()

    async def handle_result(self, action: ExampleAction, queue, *args, **kwargs):
        action.context[
            "result"
        ] = f"{action.name} Action Completed. Slept for {action.sleep_for}"


class QueueRunner:
    def __init__(self, worker=None):
        if worker is None:
            self.worker = basic_worker
        else:
            self.worker = worker
        self.queue = None

    async def do_queue(self, actions: Sequence[Type[QueueActionABC]], workers: int):
        self.queue = asyncio.Queue()
        task_workers = []
        logger.info(
            "adding %{workers}d to %{class_name}s",
            workers=workers,
            class_name=self.__class__.__name__,
        )
        for _ in range(workers):
            task = asyncio.create_task(self.worker(self.queue))
            task_workers.append(task)
        logger.info("adding %{actions}d to queue", actions=len(actions))
        start = perf_counter_ns()
        for action in actions:
            self.queue.put_nowait(action)
        await self.queue.join()
        for task in task_workers:
            task.cancel()
        await asyncio.gather(*task_workers, return_exceptions=True)
        end = perf_counter_ns()
        logger.info("Queue took %s seconds", f"{(end-start)/100000000:9f}")


async def http_worker(queue, session):
    while True:
        action = await queue.get()
        await action.do_action(queue=queue, session=session)
        # await action.handle_results(queue=queue, session=session)
        queue.task_done()


class HttpResultHandlerABC(ABC):
    def __init__(self):
        pass

    @abstractmethod
    async def handle_result(self, action, queue, response):
        pass


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


def default_object_check(init_attribute, default_constructor):
    # TODO save to utilities
    if init_attribute is None:
        return default_constructor()
    return init_attribute


class HttpAction:
    def __init__(
        self,
        name: str,
        method: str,
        url_template: str,
        request_parameters: dict = None,
        json_parameters: dict = None,
        headers=None,
        retry_on_fail: bool = True,
        retry_limit: int = 5,
        result_handlers: List[Type[HttpResultHandlerABC]] = None,
        request_config_parameters: dict = None,
        context: dict = None,
        parent_action=None,
        child_actions=None,
    ):
        self.name: str = name
        self.context = default_object_check(context, dict)
        self.result_handlers = default_object_check(result_handlers, list)
        self.method = method
        self.retry_on_fail = retry_on_fail
        self.retry_limit = retry_limit
        self.retry_count = 0
        self.request_parameters = default_object_check(request_parameters, dict)
        self.json_parameters = default_object_check(json_parameters, dict)
        self.headers = default_object_check(headers, dict)
        self.request_config_parameters = default_object_check(
            request_config_parameters, dict
        )
        self.child_actions = default_object_check(child_actions, list)
        self.parent_action = parent_action
        self.url_template = url_template
        self.url = Template(url_template).substitute(self.request_parameters)

    def __repr__(self):
        fields = self.__dict__.keys()
        field_strings = []
        for field in fields:
            stub = f"{field}: {self.__dict__[field]!r}"
            field_strings.append(stub)
        repr_string = f"{self.__class__.__name__}({', '.join(field_strings)})"
        return repr_string

    async def handle_results(self, queue, response):
        for handler in self.result_handlers:
            await handler.handle_result(
                self,
                queue,
                response,
            )

    async def do_action(self, queue, session: aiohttp.ClientSession):
        logger.debug("Doing action in %s", self.name)
        if self.retry_count >= self.retry_limit:
            return
        self.retry_count += 1
        try:
            async with session.request(
                self.method,
                self.url,
                params=self.request_parameters,
                json=self.json_parameters,
                **self.request_config_parameters,
            ) as response:
                await self.handle_results(queue, response)

        except Exception:
            # TODO better error recovery, for instance aiohttp.client_exceptions.ServerDisconnectedError
            logger.exception("Exception in do_action for %s", self.name)

    async def log_network_error(self, response, queue):
        logger.error(
            "\n Network Error for url:%s\n Error Status: %sn Response Text:\n%s\n Action:\n%s\n Response:\n%s",
            self.url,
            response.status,
            await response.text(),
            self,
            response,
        )


class PrintResponse(HttpResultHandlerABC):
    def __init__(self):
        super().__init__()

    async def handle_result(self, action, queue, response):
        print(await response.text())


class PrintPageNumber(HttpResultHandlerABC):
    def __init__(self):
        super().__init__()

    async def handle_result(self, action, queue, response):
        page_limit = response.headers.get("x-pages", None)
        page = action.request_parameters.get("page", 0)
        print(f"\npage {page} of {page_limit}")


class ResponseToJson(HttpResultHandlerABC):
    def __init__(self):
        super().__init__()

    async def handle_result(self, action, queue, response):
        logger.debug("In %s with action: %s", self.__class__.__name__, action.name)
        if response.status == 200:
            try:
                json_data = {}
                json_data = await response.json()
                # assert len(json_data) > 1
                action.context["response_json"] = json_data
            except:
                logger.exception(
                    "Error raised trying to get json from response. \nAction: %s, \nResponse: %s, \nJson_data: %s \ntext_data: %s",
                    action,
                    response,
                    json_data,
                    await response.text(),
                )
        else:
            # Signals not getting a successful response.
            action.context["response_json"] = None


class CheckForRetry(HttpResultHandlerABC):
    def __init__(self, backoff=2):
        super().__init__()
        self.backoff = backoff

    async def handle_result(self, action, queue, response):
        if response.status == 200:
            return
        if response.status == 400:
            logger.warning(
                "\nAction received response code of %s. Invalid Parameters. Fail. Action:\n%s\nResponse:\n%s",
                response.status,
                action,
                response,
            )
            raise NotImplementedError
        if response.status == 429:
            logger.warning(
                "\nAction received response code of %s. Rate Limit Exceeded. Action:\n%s\nResponse:\n%s",
                response.status,
                action,
                response,
            )
            # TODO parse return header, find rate limit, and calculate delay.
            raise NotImplementedError
        if response.status in {502, 503, 504} and action.retry_on_fail:
            if action.retry_limit >= action.retry_count:
                backoff_delay = self.backoff ** action.retry_count
                action.retry_count = action.retry_count + 1

                logger.info(
                    "\nAction received response code of %s. Retrying action with delay of %s seconds. Action.url:\n%s",
                    response.status,
                    backoff_delay,
                    action.url,
                )
                await asyncio.sleep(delay=backoff_delay)
                await queue.put(action)
            else:
                logger.warning(
                    "\nAction exceeded retry limit with no success. Action:\n%s\nResponse:\n%s",
                    action,
                    response,
                )
            return
        logger.warning(
            "\nAction failed with no attempt to retry. Action:\n%s\nResponse:\n%s",
            action,
            response,
        )


class CheckForPages(HttpResultHandlerABC):
    # NOTE original context is NOT passed to child actions
    def __init__(self):
        super().__init__()

    def make_new_actions(self, action, page_range):
        new_actions = []
        for x in range(2, page_range + 1):
            page_suffix = f"_page_{x}_of_{page_range}"
            new_action = HttpAction(
                name=action.name + page_suffix,
                method=action.method,
                url_template=action.url_template,
                request_parameters=copy.deepcopy(action.request_parameters),
                json_parameters=copy.deepcopy(action.json_parameters),
                result_handlers=action.result_handlers,
                context={},
                retry_on_fail=action.retry_on_fail,
                retry_limit=action.retry_limit,
                request_config_parameters=copy.deepcopy(
                    action.request_config_parameters
                ),
                parent_action=action
                # url_keys=copy.deepcopy(action.url_keys),
            )
            # new_action.name = action.name + page_suffix
            new_action.request_parameters["page"] = x
            new_action.parent_action = action
            action.child_actions.append(new_action)
            # print(new_action)
            new_actions.append(new_action)
        logger.info(
            "Made %s new actions to collect pages for %s", len(new_actions), action.name
        )
        return new_actions

    async def handle_result(self, action, queue, response):
        logger.debug("In %s with action: %s", self.__class__.__name__, action.name)
        if response.status == 200:
            page = action.request_parameters.get("page", None)
            if page is not None and page == 1:
                page_range = response.headers.get("x-pages", None)
                action.context["x-pages"] = page_range
                if page_range is not None:
                    page_range = int(page_range)
                    if page_range > 1:
                        new_actions = self.make_new_actions(action, page_range)
                        for new_action in new_actions:
                            logger.debug(
                                "Adding page %s of %s for action: %s",
                                new_action.request_parameters["page"],
                                page_range,
                                action.name,
                            )
                            queue.put_nowait(new_action)


class SaveResponseJsonByName(HttpResultHandlerABC):
    def __init__(self, base_path: Path):
        super().__init__()
        self.base_path = base_path

    async def handle_result(self, action, queue, response):
        file_path = self.base_path / Path(action.name + ".json")
        json_data = action.context.get("response_json", {})
        save_json(json_data, file_path, 2, False)


class SaveResponseListCsvByName(HttpResultHandlerABC):
    def __init__(self, base_path: Path, headers: List[str] = None):
        super().__init__()
        self.base_path = base_path
        self.headers = headers

    async def handle_result(self, action, queue, response):
        file_path = self.base_path / Path(action.name + ".csv")
        json_data = action.context.get("response_json", [])
        rows_saved = write_list_to_csv(
            json_data, file_path, True, has_header=False, headers=self.headers
        )
        print("rows saved", rows_saved)


class SaveResponseDictCsvByName(HttpResultHandlerABC):
    def __init__(self, base_path: Path):
        super().__init__()
        self.base_path = base_path

    async def handle_result(self, action, queue, response):
        file_path = self.base_path / Path(action.name + ".csv")
        json_data = action.context.get("response_json", {})
        write_list_of_dicts_to_csv(json_data, file_path, True)


class SaveResponseTextByName(HttpResultHandlerABC):
    def __init__(self, base_path: Path):
        super().__init__()
        self.base_path = base_path

    async def handle_result(self, action, queue, response):
        file_path = self.base_path / Path(action.name + ".csv")
        data = await response.text()
        save_string(data, file_path)


class SingletonListToListOfDicts(HttpResultHandlerABC):
    # TODO change this to general list to dict converter, handle more than one list field. zip?
    def __init__(self, key):
        super().__init__()
        self.key = key

    async def handle_result(self, action, queue, response):
        json_data = action.context.get("response_json", [])
        new_data = [{self.key: x} for x in json_data]
        action.context["response_json"] = new_data


def save_string(data: str, file_path: Path) -> bool:
    """Save a string. Makes parent directories if they don't exist.

    Traps all errors and prints them to std out.

    Arguments:
        data {str} -- The string to save
        file_path {Path} -- Path to the saved file.

    Returns:
        bool -- True if successful
    """
    try:
        if not file_path.parent.exists():
            file_path.parent.mkdir(parents=True)
        with open(file_path, "w") as out_file:
            out_file.write(data)
    except Exception as e:
        print(e)
        return False
    return True


def write_list_to_csv(
    data: Iterable[Sequence],
    file_path: Path,
    parents=False,
    exist_ok=True,
    has_header: bool = True,
    headers: Optional[Sequence[str]] = None,
) -> int:
    """
    Writes an iterator of lists to a file in csv format.

    Parameters
    ----------
    data : Iterable[Sequence]
        [description]
    file_path : Path
        [description]
    parents : bool, optional
        [description], by default False
    exist_ok : bool, optional
        [description], by default True
    has_header : bool, optional
        First row of supplied data is the header, by default True
    headers : Optional[Sequence[str]], optional
        Headers to use if not supplied in data, by default None

    Returns
    -------
    int
        Rows saved, not including a header

    Raises
    ------
    ValueError
        Number of items in a row does not match number of headers.
    """
    if parents:
        file_path.parent.mkdir(parents=parents, exist_ok=exist_ok)
    with file_path.open("w", encoding="utf8", newline="") as file_out:
        writer = csv.writer(file_out)
        iterable_data = iter(data)

        if has_header:
            header_row = next(iterable_data)
            writer.writerow(header_row)
        else:
            if headers is not None:
                header_row = headers
                writer.writerow(header_row)
            else:
                header_row = []
        total_count = 0
        for count, item in enumerate(iterable_data):
            if count > 0 and has_header:
                if len(header_row) > 0 and len(header_row) != len(item):
                    raise ValueError(
                        f"Header has {len(header_row)} but row has {len(item)} items"
                    )
                writer.writerow(item)
                total_count = count
    return total_count + 1


def write_list_of_dicts_to_csv(
    data: Sequence[Dict[str, Any]], file_path: Path, parents=False, exist_ok=True
) -> int:
    """
    Save a list of dicts to csv. Makes parent directories if they don't exist.

    Parameters
    ----------
    data : Sequence[Dict[str, Any]]
        Data to save.
    file_path : Path
        Path to saved file. Existing files will be overwritten.
    parents : bool, optional
        Make parent directories if they don't exist. As used by `Path.mkdir`, by default False
    exist_ok : bool, optional
        Suppress exception if parent directory exists as directory. As used by `Path.mkdir`, by default True

    Returns
    -------
    int
        records writen.

    Raises
    ------
    Exception
        Any exception that can be raised from Path.mkdir or Path.open
    """
    if parents:
        file_path.parent.mkdir(parents=parents, exist_ok=exist_ok)
    with file_path.open("w", encoding="utf8", newline="") as file_out:
        writer = csv.DictWriter(file_out, fieldnames=list(data[0].keys()))
        writer.writeheader()
        total_count = 0
        for count, item in enumerate(data):
            writer.writerow(item)
            total_count = count
    return total_count + 1


def save_json(data: Any, file_path: Path, indent=2, sort_keys=False) -> bool:
    try:
        if not file_path.parent.exists():
            file_path.parent.mkdir(parents=True)
        with open(file_path, "w") as json_file:
            json.dump(data, json_file, indent=indent, sort_keys=sort_keys)
        return True
    except Exception as e:
        logger.exception("Error trying to save json data to %s", file_path)
        raise e


def run_actions(actions, workers: int):
    runner = HttpQueueRunner()
    asyncio.run(runner.do_queue(actions, workers))


def consolidate_page_data_json(parent_action):
    pages = [*parent_action.context["response_json"]]
    for child_action in parent_action.child_actions:
        pages.extend(child_action.context["response_json"])
    return pages


def consolidate_actions_json(actions, skip_empty=False):
    if skip_empty:
        logger.info("skip empty")
        result = [
            action.context["response_json"]
            for action in actions
            if action.context["response_json"]
        ]
    else:
        result = [action.context["response_json"] for action in actions]
    return result


# https://github.com/aio-libs/aiohttp/issues/850#issuecomment-210883478

# HTTP_STATUS_CODES_TO_RETRY = [500, 502, 503, 504]
# class FailedRequest(Exception):
#     """
#     A wrapper of all possible exception during a HTTP request
#     """
#     code = 0
#     message = ''
#     url = ''
#     raised = ''

#     def __init__(self, *, raised='', message='', code='', url=''):
#         self.raised = raised
#         self.message = message
#         self.code = code
#         self.url = url

#         super().__init__("code:{c} url={u} message={m} raised={r}".format(
#             c=self.code, u=self.url, m=self.message, r=self.raised))


# async def send_http(session, method, url, *,
#                     retries=1,
#                     interval=0.9,
#                     backoff=3,
#                     read_timeout=15.9,
#                     http_status_codes_to_retry=HTTP_STATUS_CODES_TO_RETRY,
#                     **kwargs):
#     """
#     Sends a HTTP request and implements a retry logic.

#     Arguments:
#         session (obj): A client aiohttp session object
#         method (str): Method to use
#         url (str): URL for the request
#         retries (int): Number of times to retry in case of failure
#         interval (float): Time to wait before retries
#         backoff (int): Multiply interval by this factor after each failure
#         read_timeout (float): Time to wait for a response
#     """
#     backoff_interval = interval
#     raised_exc = None
#     attempt = 0

#     if method not in ['get', 'patch', 'post']:
#         raise ValueError

#     if retries == -1:  # -1 means retry indefinitely
#         attempt = -1
#     elif retries == 0: # Zero means don't retry
#         attempt = 1
#     else:  # any other value means retry N times
#         attempt = retries + 1

#     while attempt != 0:
#         if raised_exc:
#             log.error('caught "%s" url:%s method:%s, remaining tries %s, '
#                     'sleeping %.2fsecs', raised_exc, method.upper(), url,
#                     attempt, backoff_interval)
#             await asyncio.sleep(backoff_interval)
#             # bump interval for the next possible attempt
#             backoff_interval = backoff_interval * backoff
#         log.info('sending %s %s with %s', method.upper(), url, kwargs)
#         try:
#             with aiohttp.Timeout(timeout=read_timeout):
#                 async with getattr(session, method)(url, **kwargs) as response:
#                     if response.status == 200:
#                         try:
#                             data = await response.json()
#                         except json.decoder.JSONDecodeError as exc:
#                             log.error(
#                                 'failed to decode response code:%s url:%s '
#                                 'method:%s error:%s response:%s',
#                                 response.status, url, method.upper(), exc,
#                                 response.reason
#                             )
#                             raise aiohttp.errors.HttpProcessingError(
#                                 code=response.status, message=exc.msg)
#                         else:
#                             log.info('code:%s url:%s method:%s response:%s',
#                                     response.status, url, method.upper(),
#                                     response.reason)
#                             raised_exc = None
#                             return data
#                     elif response.status in http_status_codes_to_retry:
#                         log.error(
#                             'received invalid response code:%s url:%s error:%s'
#                             ' response:%s', response.status, url, '',
#                             response.reason
#                         )
#                         raise aiohttp.errors.HttpProcessingError(
#                             code=response.status, message=response.reason)
#                     else:
#                         try:
#                             data = await response.json()
#                         except json.decoder.JSONDecodeError as exc:
#                             log.error(
#                                 'failed to decode response code:%s url:%s '
#                                 'error:%s response:%s', response.status, url,
#                                 exc, response.reason
#                             )
#                             raise FailedRequest(
#                                 code=response.status, message=exc,
#                                 raised=exc.__class__.__name__, url=url)
#                         else:
#                             log.warning('received %s for %s', data, url)
#                             print(data['errors'][0]['detail'])
#                             raised_exc = None
#         except (aiohttp.errors.ClientResponseError,
#                 aiohttp.errors.ClientRequestError,
#                 aiohttp.errors.ClientOSError,
#                 aiohttp.errors.ClientDisconnectedError,
#                 aiohttp.errors.ClientTimeoutError,
#                 asyncio.TimeoutError,
#                 aiohttp.errors.HttpProcessingError) as exc:
#             try:
#                 code = exc.code
#             except AttributeError:
#                 code = ''
#             raised_exc = FailedRequest(code=code, message=exc, url=url,
#                                     raised=exc.__class__.__name__)
#         else:
#             raised_exc = None
#             break

#         attempt -= 1

#     if raised_exc:
#         raise raised_exc
