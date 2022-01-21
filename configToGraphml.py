
import json

from Nodes.NodeEngine import NodeEngine

from lxml import etree


engine = NodeEngine()

with open("configuration.json") as f:
    loaded_data = json.loads(f.read())
    engine.deserialize(loaded_data)

namespaces = {
    None: "http://graphml.graphdrawing.org/xmlns",
    "java": "http://www.yworks.com/xml/yfiles-common/1.0/java",
    "sys": "http://www.yworks.com/xml/yfiles-common/markup/primitives/2.0",
    "x": "http://www.yworks.com/xml/yfiles-common/markup/2.0",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "y": "http://www.yworks.com/xml/graphml",
    "yed": "http://www.yworks.com/xml/yed/3",
}


y_n = "{%s}" % namespaces["y"]
root = etree.Element("graphml", nsmap=namespaces)

graph = etree.SubElement(root, "graph", edgedefault = "directed")

key = etree.Element("key")
key.set("for", "node")
key.set("id", "d5")
key.set("yfiles.type", "nodegraphics")
root.append(key)


for node_id, node in engine.getAllNodes().items():
    node_element = etree.SubElement(graph, "node", id = node_id)
    data = etree.SubElement(node_element, "data", key = "d5")
    shape_node = etree.SubElement(data, y_n + "ShapeNode")
    etree.SubElement(shape_node, y_n + "Geometry", height = "100", width = "100", y = "100", x = "100")
    etree.SubElement(shape_node, y_n + "Fill", color="#FFCC00", transparent="false")
    etree.SubElement(shape_node, y_n + "BorderStyle", color="#000000", type="line", width ="1.0")
    etree.SubElement(shape_node, y_n + "NodeLabel").text = node_id
    etree.SubElement(shape_node, y_n + "Shape", type = "Rectangle")


for node_id, node in engine.getAllNodes().items():
    for connection in node.getAllOutgoingConnections():
        edge = etree.SubElement(graph, "edge", id = f"{node_id}_{connection.target.getId()}_{connection.resource_type}", source = node_id, target=connection.target.getId())

et = etree.ElementTree(root)
et.write("output.graphml", pretty_print = True)
