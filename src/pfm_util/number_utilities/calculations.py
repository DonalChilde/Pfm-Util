from typing import Union


def percent_difference(foo: Union[int, float], bar: Union[int, float]) -> float:
    if bar == 0:
        return 0
    diff = foo - bar
    return diff / bar


def safe_div(num: Union[int, float], denom: Union[int, float]) -> float:
    # https://stackoverflow.com/a/27317595/105844
    num = float(num)
    denom = float(denom)
    if not denom:
        return 0
    # print(f"{num},{denom}")
    result = num / denom
    return result
