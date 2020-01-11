from unittest.mock import MagicMock

from Nodes.Node import Node
from Nodes.NodeHistory import NodeHistory


def test_resourcesGainedHistory():
    node = Node("blarg")
    node.getResourcesReceivedThisTick = MagicMock(side_effect = [{"energy": 20}, {"energy": 21}] )
    history = NodeHistory(node)

    node.postUpdate()
    assert history.getResourcesGainedHistory() == {"energy": [20]}
    node.postUpdate()

    assert history.getResourcesGainedHistory() == {"energy": [20, 21]}


def test_resourcesProducedHistory():
    node = Node("blarg!")
    node.getResourcesProducedThisTick = MagicMock(side_effect = [{"energy": 200}, {"energy": 900}])
    history = NodeHistory(node)

    node.postUpdate()
    assert history.getResourcesProducedHistory() == {"energy": [200]}
    node.postUpdate()

    assert history.getResourcesProducedHistory() == {"energy": [200, 900]}


def test_getResourcesRequiredPerTick():
    node = Node("blarg!")
    node.getResourcesRequiredPerTick = MagicMock(return_value = {"fuel": 200})
    history = NodeHistory(node)

    node.postUpdate()
    assert history.getResourcesGainedHistory() == {"fuel": [0]}
    node.postUpdate()
    assert history.getResourcesGainedHistory() == {"fuel": [0, 0]}