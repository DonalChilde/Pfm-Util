import logging
from asyncio.queues import Queue
from string import Template
from typing import TYPE_CHECKING, Dict, Optional, Sequence, Union

from aiohttp import ClientResponse, ClientSession

from pfmsoft.util.async_actions import (
    AsyncAction,
    AsyncActionCallback,
    AsyncActionMessenger,
)

logger = logging.getLogger(__name__)


HTTP_STATUS_CODES_TO_RETRY = [500, 502, 503, 504]


def default_object_check(init_attribute, default_constructor):
    # TODO save to utilities
    if init_attribute is None:
        return default_constructor()
    return init_attribute


class AiohttpAction(AsyncAction):
    """
    A self contained unit of execution

    [extended_summary]

    :param AsyncAction: [description]
    :type AsyncAction: [type]
    """

    def __init__(
        self,
        queue: Queue,
        session: ClientSession,
        method: str,
        url_template: str,
        url_parameters: Optional[dict] = None,
        retry_limit: int = 0,
        context: Optional[dict] = None,
        request_kwargs: Optional[dict] = None,
        name: str = "",
        id=None,
        action_callbacks: Optional[Dict[str, Sequence[AsyncActionCallback]]] = None,
        action_messengers: Optional[Sequence[AsyncActionMessenger]] = None,
    ) -> None:
        super().__init__(
            name=name,
            id=id,
            action_callbacks=action_callbacks,
            action_messengers=action_messengers,
        )
        self.queue = queue
        self.session = session
        self.method = method
        self.url_template = url_template
        self.url_parameters: Dict = default_object_check(url_parameters, dict)
        self.url = Template(url_template).substitute(self.url_parameters)
        self.retry_limit = retry_limit
        self.response: Optional[ClientResponse] = None
        # self.response_data: Optional[Union[str, dict, bytes]] = None
        self.retry_count: int = 0
        self.request_kwargs = default_object_check(request_kwargs, dict)
        self.context = default_object_check(context, dict)
        # self.json_data = None

    async def do_action(self, *args, **kwargs):
        try:
            if self.retry_count <= self.retry_limit:
                async with self.session.request(
                    self.method, self.url, **self.request_kwargs
                ) as response:
                    self.response = response
                    await self.check_response()
            else:
                await self.fail()
        except Exception as e:
            print(e)

    async def check_response(self):
        if self.response.status == 200:
            await self.success()
        elif self.response.status in HTTP_STATUS_CODES_TO_RETRY:
            self.retry_count += 1
            await self.queue.put(self)
            await self.retry()
        else:
            await self.fail()


class AiohttpActionCallback:
    def __init__(self) -> None:
        pass

    async def do_callback(self, caller: AiohttpAction, *args, **kwargs):
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


class LogFailure(AiohttpActionCallback):
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
