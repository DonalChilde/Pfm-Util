import logging
from asyncio import Task, create_task, gather
from asyncio.queues import Queue
from time import perf_counter_ns
from typing import TYPE_CHECKING, Any, Coroutine, Dict, Optional, Sequence

from rich import inspect, print

logger = logging.getLogger(__name__)


async def do_async_action_queue(
    actions: Sequence["AsyncAction"],
    workers: Sequence[Coroutine],
    queue: Queue,
):
    logger.info(
        "Starting queue with %s workers and %s actions", len(workers), len(actions)
    )
    start = perf_counter_ns()
    worker_tasks = []
    for worker in workers:
        worker_task: Task = create_task(worker)
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


class QueueWorker:
    """
    - timing
    - backoff?
    - untrapped errors

    [extended_summary]
    """

    def __init__(self) -> None:
        pass

    def get_worker(self, queue: Queue):
        async def consumer(queue):
            while True:
                action: AsyncAction = await queue.get()
                try:
                    await action.do_action()
                except Exception as ex:
                    print(ex)
                queue.task_done()

        worker = consumer(queue)
        return worker


class AsyncActionCallback:
    def __init__(self) -> None:
        pass

    async def do_callback(self, caller: "AsyncAction", *args, **kwargs):
        pass


class AsyncActionMessenger:
    def __init__(self) -> None:
        pass

    async def action_message(self, message, *args, **kwargs):
        pass


class AsyncAction:
    def __init__(
        self,
        name: str = "",
        id_: Optional[str] = None,
        action_callbacks: Optional[Dict[str, Sequence[AsyncActionCallback]]] = None,
        action_messengers: Optional[Sequence[AsyncActionMessenger]] = None,
    ) -> None:
        self.name = name
        self.id = id_
        self.action_callbacks: Optional[
            Dict[str, Sequence[AsyncActionCallback]]
        ] = action_callbacks
        self.action_messengers: Optional[
            Sequence[AsyncActionMessenger]
        ] = action_messengers
        self.result: Any = None

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

    async def check_result(self, *args, **kwargs):
        raise NotImplementedError

    async def do_action(self, *args, **kwargs):
        raise NotImplementedError
