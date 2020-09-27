import asyncio
from pathlib import Path

# import aiohttp
import pytest

from pfm_util.http_async_queue.async_queue import (
    CheckForPages,
    ExampleAction,
    ExampleHandler,
    HttpAction,
    HttpQueueRunner,
    PrintResponse,
    QueueRunner,
    ResponseToJson,
    basic_worker,
    # save_processed_response,
    # save_response,
    # save_response_to_csv,
    # save_response_to_json,
    PrintPageNumber,
    # StorePageTextOnParentAction,
    # StorePageJsonOnParentAction,
)

# from tests.asyncQueueRunner import market_history as MH


def test_basic_runner():
    actions = []

    for x in range(20):
        handler = ExampleHandler()
        action = ExampleAction(x, result_handlers=[handler])
        actions.append(action)

    runner = QueueRunner(basic_worker)
    asyncio.run(runner.do_queue(actions, 5))
    assert len(actions) == 20
    assert "Action Completed" in actions[0].context["result"]
    print(actions[0].context["result"])
    # assert False


def test_get_json():
    actions = []
    url_template = "https://esi.evetech.net/v1/universe/regions/"
    request_parameters = {"datasource": "tranquility"}
    action = HttpAction(
        name="test",
        method="GET",
        url_template=url_template,
        request_parameters=request_parameters,
        # store_response_text=True,
        result_handlers=[
            PrintResponse(),
            ResponseToJson(),
        ],
        context={},
    )
    # action.context["save_path"] = Path("~/tmp/region_ids.json").expanduser()
    actions.append(action)
    runner = HttpQueueRunner()
    asyncio.run(runner.do_queue(actions, 5))
    print(actions[0])
    assert isinstance(action.context["response_json"], list)
    assert len(action.context["response_json"]) == 106


# def test_get_region_orders_text():
#     actions = []
#     server_url = "https://esi.evetech.net"
#     region_id = "10000033"
#     url_template = "/v1/markets/${region_id}/orders/"
#     request_params = {"datasource": "tranquility", "page": 1, "order_type": "all"}
#     action = HttpAction(
#         name="region test",
#         method="GET",
#         url_template=server_url + url_template,
#         request_params=request_params,
#         result_handlers=[CheckForPages(), PrintPageNumber(), StorePageText()],
#         url_keys={"region_id": region_id},
#     )
#     actions.append(action)
#     runner = HttpQueueRunner()
#     asyncio.run(runner.do_queue(actions, 20))

#     assert len(action.context["pages"]) > 5


# def test_get_region_orders_json():
#     actions = []
#     server_url = "https://esi.evetech.net"
#     region_id = "10000033"
#     url_template = f"/v1/markets/{region_id}/orders/"
#     request_params = {"datasource": "tranquility", "page": 1, "order_type": "all"}
#     action = HttpAction(
#         name="region test",
#         method="GET",
#         url_template=server_url + url_template,
#         request_params=request_params,
#         result_handlers=[CheckForPages(), PrintPageNumber(), StorePageJson()],
#         url_keys={"region_id": region_id},
#     )

#     # action.context["region_id"] = region_id
#     actions.append(action)
#     runner = HttpQueueRunner()
#     asyncio.run(runner.do_queue(actions, 20))

#     assert len(action.context["pages"]) > 5


async def region_order_save_path(action: HttpAction, response, queue):
    region_id = action.context.get("region_id", 0)
    page = action.request_params.get("page", 0)
    page_limit = response.headers.get("x-pages", 0)
    save_path = Path(
        f"~/tmp/market_orders_{region_id}.{page}_of_{page_limit}.csv"
    ).expanduser()
    return save_path
