
import pytest
from binary_search import binary_search


def test_target_present():
    arr = [2, 4, 6, 8, 10, 12, 14]
    assert binary_search(arr, 10) == 4


def test_target_absent():
    arr = [2, 4, 6, 8, 10]
    assert binary_search(arr, 7) == -1


def test_empty_array():
    arr = []
    assert binary_search(arr, 5) == -1


def test_single_element_present():
    arr = [10]
    assert binary_search(arr, 10) == 0


def test_single_element_absent():
    arr = [10]
    assert binary_search(arr, 5) == -1


def test_first_element():
    arr = [2, 4, 6, 8, 10]
    assert binary_search(arr, 2) == 0


def test_last_element():
    arr = [2, 4, 6, 8, 10]
    assert binary_search(arr, 10) == 4
