import base64
import json
from pathlib import Path

from Nodes.ComputationNode import ComputationNode
from Nodes.FluidCooler import FluidCooler
from Nodes.Generator import Generator
from Nodes.NodeEngine import NodeEngine

from lxml import etree

from Nodes.OilExtractor import OilExtractor
from Nodes.PlantPress import PlantPress
from Nodes.ResourceStorage import ResourceStorage
from Nodes.Toilets import Toilets
from Nodes.Valve import Valve
from Nodes.WaterPurifier import WaterPurifier

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

default_node_width = 100
default_node_height = 100


y_n = "{%s}" % namespaces["y"]
yed_n = "{%s}" % namespaces["yed"]
root = etree.Element("graphml", nsmap=namespaces)
key_d5 = etree.Element("key")
key_d5.set("for", "node")
key_d5.set("id", "d5")
key_d5.set("yfiles.type", "nodegraphics")
root.append(key_d5)


key_d7 = etree.Element("key")
key_d7.set("for", "graphml")
key_d7.set("id", "d7")
key_d7.set("yfiles.type", "resources")
root.append(key_d7)

key_d9 = etree.Element("key")
key_d9.set("for", "edge")
key_d9.set("id", "d9")
key_d9.set("yfiles.type", "edgegraphics")
root.append(key_d9)


key_d10 = etree.Element("key")
key_d10.set("for", "edge")
key_d10.set("id", "d10")
key_d10.set("yfiles.type", "edgegraphics")
root.append(key_d10)

graph = etree.SubElement(root, "graph", edgedefault = "directed")


# Prepare all the image files
resources_data = etree.Element("data", key = "d7")
resources = etree.SubElement(resources_data, y_n + "Resources")

images = ["images/FluidStorage.png", "images/Battery.png", "images/SolidStorage.png", "images/Generator.png",
          "images/Lights.png", "images/FluidCooler.png", "images/Valve.png", "images/Computer.png",
          "images/WaterPurifier.png", "images/SolarPanel.png", "images/PlantPress.png", "images/Toilet.png",
          "images/Extractor.png"]


for i, image in enumerate(images):
    with open(image, "rb") as f:
        encoded_image = base64.b64encode(f.read())
        etree.SubElement(resources, y_n + "Resource", id = str(i), type = "java.awt.image.BufferedImage").text = encoded_image
        icon_name = Path(image).stem
        icon_resource = etree.SubElement(resources, y_n + "Resource", id = f"{icon_name}Icon")
        scaled_icon = etree.SubElement(icon_resource, yed_n + "ScaledIcon", xScale = "0.25", yScale = "0.25")
        etree.SubElement(scaled_icon, yed_n + "ImageIcon", image = str(i))



# Add all the nodes
for node_id, node in engine.getAllNodes().items():
    node_element = etree.SubElement(graph, "node", id = node_id)
    data = etree.SubElement(node_element, "data", key = "d5")
    shape_node = etree.SubElement(data, y_n + "ShapeNode")
    etree.SubElement(shape_node, y_n + "Geometry", height = str(default_node_height), width = str(default_node_width), y = "100", x = "100")
    etree.SubElement(shape_node, y_n + "Fill", color="#FFCC00", transparent="false")
    etree.SubElement(shape_node, y_n + "BorderStyle", color="#000000", type="line", width ="1.0")

    icon_data = ""
    # If the node is a store unit, add the storage icon
    if type(node) == ResourceStorage:
        # Yeah, it's not the cleanest solution, but whatever.
        if node._resource_type != "energy":
            if node._resource_type in ["fuel", "water", "oxygen", "dirty_water", "plant_oil"]:
                icon_data = "FluidStorageIcon"
            else:
                icon_data = "SolidStorageIcon"
        else:
            icon_data = "BatteryIcon"
    elif type(node) == Generator:
        icon_data = "GeneratorIcon"

    elif "lights" in node.getId():
        icon_data = "LightsIcon"
    elif type(node) == FluidCooler:
        icon_data = "FluidCoolerIcon"
    elif type(node) == Valve:
        icon_data = "ValveIcon"
    elif type(node) == ComputationNode or "scanner" in node.getId():
        icon_data = "ComputerIcon"
    elif type(node) == WaterPurifier:
        icon_data = "WaterPurifierIcon"
    elif node.getId() == "solar_panel":
        icon_data = "SolarPanelIcon"
    elif type(node) == PlantPress:
        icon_data = "PlantPressIcon"
    elif type(node) == Toilets:
        icon_data = "ToiletIcon"
    elif type(node) == OilExtractor:
        icon_data = "ExtractorIcon"
    etree.SubElement(shape_node, y_n + "NodeLabel", iconData= icon_data).text = node_id
    etree.SubElement(shape_node, y_n + "Shape", type = "Rectangle")


def getResourceColor(resource_type):
    if resource_type == "water":
        return "#0000ff"
    if resource_type == "energy":
        return "#ffff00"
    if resource_type == "fuel":
        return "#A52A2A"
    if resource_type == "plants":
        return "#00ff00"
    return "#000000"

# Add all the connections
for node_id, node in engine.getAllNodes().items():
    for connection in node.getAllOutgoingConnections():
        edge = etree.SubElement(graph, "edge", id = f"{node_id}_{connection.target.getId()}_{connection.resource_type}", source = node_id, target=connection.target.getId())
        data_key = etree.SubElement(edge, "data", key = "d9")
        poly_line_edge = etree.SubElement(data_key, y_n + "PolyLineEdge")
        color = getResourceColor(connection.resource_type)
        etree.SubElement(poly_line_edge, y_n + "LineStyle", color = color, type="line", width = "1.0")

root.append(resources_data)
et = etree.ElementTree(root)
et.write("output.graphml", pretty_print = True)
