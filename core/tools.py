"""
File:
tools.py

some useful tools (general python stuff)

Author:
Nilusink
"""
from copy import deepcopy
import typing as tp


def remove_all(input_list: list, e: tp.Any, use_deepcopy: bool = False) -> list:
    """
    remove all occurrences of an object in a list
    """
    if use_deepcopy:
        input_list = deepcopy(input_list)

    while e in input_list:
        input_list.remove(e)

    return input_list
