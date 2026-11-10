
import pytest

from graph_algorithms import bfs, dfs, dijkstra, has_cycle


@pytest.fixture
def simple_graph():
    return {
        "A": ["B", "C"],
        "B": ["A", "D", "E"],
        "C": ["A", "F"],
        "D": ["B"],
        "E": ["B", "F"],
        "F": ["C", "E"]
    }


def test_bfs(simple_graph):
    assert bfs(simple_graph, "A") == [
        "A", "B", "C", "D", "E", "F"
    ]


def test_dfs(simple_graph):
    assert dfs(simple_graph, "A") == [
        "A", "B", "D", "E", "F", "C"
    ]


def test_bfs_disconnected():
    graph = {
        1: [2],
        2: [1],
        3: [4],
        4: [3]
    }

    assert bfs(graph, 1) == [1, 2]


def test_dijkstra():
    graph = {
        "A": [("B", 4), ("C", 1)],
        "B": [("A", 4), ("C", 2), ("D", 1)],
        "C": [("A", 1), ("B", 2), ("D", 5)],
        "D": [("B", 1), ("C", 5)],
        "E": []
    }

    assert dijkstra(graph, "A") == {
        "A": 0,
        "B": 3,
        "C": 1,
        "D": 4,
        "E": float("inf")
    }


def test_dijkstra_unreachable_node():
    graph = {
        1: [(2, 5)],
        2: [(1, 5)],
        3: []
    }

    result = dijkstra(graph, 1)

    assert result[3] == float("inf")


def test_dijkstra_rejects_negative_weights():
    graph = {
        "A": [("B", -2)],
        "B": []
    }

    with pytest.raises(ValueError):
        dijkstra(graph, "A")


def test_cycle_detection_true():
    graph = {
        1: [2, 3],
        2: [1, 3],
        3: [1, 2]
    }

    assert has_cycle(graph) is True


def test_cycle_detection_false():
    graph = {
        1: [2],
        2: [1, 3],
        3: [2],
        4: []
    }

    assert has_cycle(graph) is False


def test_bfs_invalid_start():
    with pytest.raises(ValueError):
        bfs({"A": ["B"], "B": ["A"]}, "X")


def test_dfs_invalid_start():
    with pytest.raises(ValueError):
        dfs({"A": ["B"], "B": ["A"]}, "X")


def test_dijkstra_invalid_start():
    with pytest.raises(ValueError):
        dijkstra({"A": []}, "X")
