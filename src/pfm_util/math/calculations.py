from typing import Callable, Union


def percent_difference(foo: Union[int, float], bar: Union[int, float]) -> float:
    """
    Calculate the percent difference between two numbers.

    If the second number is 0, will return zero instead of DivisionByZero exception.

    :param foo: [description]
    :param bar: [description]
    :return: [description]
    """
    diff = foo - bar
    return safe_div(diff, bar)


def safe_div(num: Union[int, float], denom: Union[int, float]) -> float:
    """
    Return 0 instead of raising DivisionByZero exception when denom is 0.

    :param num: [description]
    :param denom: [description]
    :return: [description]
    """
    # https://stackoverflow.com/a/27317595/105844

    if not denom:
        return 0
    result = num / denom

    return result


def percent_function(
    percent: float, precision: int
) -> Callable[[Union[int, float]], float]:
    def func(num: Union[int, float]):
        return round(num * percent, precision)

    return func
