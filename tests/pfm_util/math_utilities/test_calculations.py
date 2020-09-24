import logging
import pytest

from pfm_util.math_utilities import calculations

#### setting up logger ####
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def test_percent_difference(caplog):
    caplog.set_level(logging.DEBUG)
    value_1 = 5
    value_2 = 10
    per_diff = calculations.percent_difference(value_1, value_2)
    logging.debug("Percent Difference of %s and %s is: %s", value_1, value_2, per_diff)
    assert per_diff == -0.5

    value_1 = 5
    value_2 = 0
    per_diff = calculations.percent_difference(value_1, value_2)
    logging.debug("Percent Difference of %s and %s is: %s", value_1, value_2, per_diff)
    assert per_diff == 0

    value_1 = 0
    value_2 = 5
    per_diff = calculations.percent_difference(value_1, value_2)
    logging.debug("Percent Difference of %s and %s is: %s", value_1, value_2, per_diff)
    assert per_diff == -1


def test_safe_div(caplog):
    caplog.set_level(logging.DEBUG)

    numerator = 1
    denominator = 3
    result = calculations.safe_div(numerator, denominator)
    assert result == pytest.approx(1 / 3)

    numerator = 1
    denominator = 0
    result = calculations.safe_div(numerator, denominator)
    assert result == pytest.approx(0)

    numerator = 4
    denominator = 2
    result = calculations.safe_div(numerator, denominator)
    assert result == 2.0
