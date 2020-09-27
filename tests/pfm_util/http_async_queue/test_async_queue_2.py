import logging

import pytest

from pfm_util.http_async_queue.async_queue_2 import (
    HttpActionText,
    HttpQueueRunner,
    run_actions,
)


def test_get(caplog):
    caplog.set_level(logging.INFO)
    host = "https://esi.evetech.net"
    url = host + "/v1/universe/types/"
    action = HttpActionText(name="test", method="get", url_template=url, url_params={})
    actions = [action]

    run_actions(actions, workers=1)
    assert action.response.status == 200


def test_get_404(caplog):
    caplog.set_level(logging.INFO)
    host = "https://esi.evetech.net"
    url = host + "/v1/universe/types2/"
    action = HttpActionText(name="test", method="get", url_template=url, url_params={})
    actions = [action]

    run_actions(actions, workers=1)
    assert action.response.status == 404
