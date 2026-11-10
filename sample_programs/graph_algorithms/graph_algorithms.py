
import heapq
from collections import deque


def bfs(graph, start):
    if start not in graph:
        raise ValueError("Starting node does not exist")

    visited = {start}
    queue = deque([start])
    result = []

    while queue:
        node = queue.popleft()
        result.append(node)

        for neighbour in graph[node]:
            if neighbour not in visited:
                visited.add(neighbour)
                queue.append(neighbour)

    return result


def dfs(graph, start):
    if start not in graph:
        raise ValueError("Starting node does not exist")

    visited = set()
    result = []

    def explore(node):
        visited.add(node)
        result.append(node)

        for neighbour in graph[node]:
            if neighbour not in visited:
                explore(neighbour)

    explore(start)
    return result


def dijkstra(graph, start):
    if start not in graph:
        raise ValueError("Starting node does not exist")

    for neighbours in graph.values():
        for neighbour, weight in neighbours:
            if weight < 0:
                raise ValueError("Negative edge weights are not supported")

    distances = {node: float("inf") for node in graph}
    distances[start] = 0

    priority_queue = [(0, start)]

    while priority_queue:
        current_distance, node = heapq.heappop(priority_queue)

        if current_distance > distances[node]:
            continue

        for neighbour, weight in graph[node]:
            new_distance = current_distance + weight

            if new_distance < distances[neighbour]:
                distances[neighbour] = new_distance
                heapq.heappush(
                    priority_queue,
                    (new_distance, neighbour)
                )

    return distances


def has_cycle(graph):
    visited = set()

    def explore(node, parent):
        visited.add(node)

        for neighbour in graph[node]:
            if neighbour not in visited:
                if explore(neighbour, node):
                    return True
            elif neighbour != parent:
                return True

        return False

    for node in graph:
        if node not in visited:
            if explore(node, None):
                return True

    return False
