from pylatex import Document, Package

from Nodes.Generator import Generator
from Nodes.HydroponicsBay import HydroponicsBay
from Nodes.LaTeXGenerator import LaTeXGenerator
from Nodes.Node import Node
from Nodes.ResourceStorage import ResourceStorage

doc = Document('basic')
doc.packages.append(Package('float'))

test_generator = Generator("test_generator", fuel_type = "fuel", label = "Primary generator", custom_description = "This is the main generator!")
test_generator.ensureSaneValues()
test_fuel_storage = ResourceStorage("fuel_storage", "fuel", 100, 1000)

test_fuel_storage.connectWith("fuel", test_generator)

generator = LaTeXGenerator()
generator.addNode(Node("test_node"))
generator.addNode(HydroponicsBay("hydroponics"))
generator.addNode(test_generator)
generator.addNode(test_fuel_storage)
generator.addNode(Generator("test_generator2", label = "Secondary generator", custom_description = "This is the secondary generator"))
generator.fillDocument(doc)

doc.generate_pdf("manual", clean_tex=False)