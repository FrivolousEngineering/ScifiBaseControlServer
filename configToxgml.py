
import xml.etree.ElementTree as ET
import json

from Nodes.NodeEngine import NodeEngine


# Convert configuration files to rough xgml files
# The idea is to create a very rough xgml file so that it can be ordered by "yEd"


def _indent(elem, level = 0):
    """Helper function for pretty-printing XML because ETree is stupid"""

    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            _indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


engine = NodeEngine()

with open("configuration.json") as f:
    loaded_data = json.loads(f.read())
    engine.deserialize(loaded_data)


root = ET.Element("section", name = "xgml")
ET.SubElement(root, "attribute", key = "Creator", type = "String").text = "Custom"
ET.SubElement(root, "attribute", key = "Version", type = "String").text = "Whatever"

graph = ET.SubElement(root, "section", name = "graph")
ET.SubElement(graph, "attribute", key = "hierarchic", type = "int").text = "1"
ET.SubElement(graph, "attribute", key = "directed", type = "int").text = "1"


node_number_id_mapping = dict()

node_id_number = 0
for node_id, node in engine.getAllNodes().items():
    node_element = ET.SubElement(graph, "section", name = "node")
    ET.SubElement(node_element, "attribute", key = "id", type = "int").text = str(node_id_number)
    ET.SubElement(node_element, "attribute", key = "label", type = "String").text = node_id

    graphics = ET.SubElement(node_element, "section", name = "graphics")
    ET.SubElement(graphics, "attribute", key="x", type="double").text = "100"
    ET.SubElement(graphics, "attribute", key="y", type="double").text = "100"
    ET.SubElement(graphics, "attribute", key="w", type="double").text = "100"
    ET.SubElement(graphics, "attribute", key="h", type="double").text = "100"
    ET.SubElement(graphics, "attribute", key="type", type="String").text = "rectangle"
    ET.SubElement(graphics, "attribute", key="outline", type="string").text = "#000000"
    ET.SubElement(graphics, "attribute", key="fill", type="string").text = "#FFCC00"
    node_number_id_mapping[node_id] = node_id_number
    node_id_number += 1


for node_id, node in engine.getAllNodes().items():
    for connection in node.getAllOutgoingConnections():
        edge_element = ET.SubElement(graph, "section", name="edge")
        ET.SubElement(edge_element, "attribute", key="source", type="int").text = str(node_number_id_mapping[node_id])
        ET.SubElement(edge_element, "attribute", key="target", type="int").text = str(node_number_id_mapping[connection.target.getId()])

        graphics = ET.SubElement(edge_element, "section", name="graphics")
        ET.SubElement(graphics, "attribute", key="fill", type="string").text = "#000000"
        ET.SubElement(graphics, "attribute", key="targetArrow", type="string").text = "standard"


'''<section name="edge">
    <attribute key="source" type="int">0</attribute>
    <attribute key="target" type="int">1</attribute>
    <section name="graphics">
        <attribute key="fill" type="String">#000000</attribute>
        <attribute key="targetArrow" type="String">standard</attribute>
</section>'''


_indent(root)
tree = ET.ElementTree(root)
tree.write("output.xgml")
#for node in engine.getAllNodes():

