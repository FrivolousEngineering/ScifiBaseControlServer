from pylatex import Document

from Nodes.Generator import Generator
from Nodes.HydroponicsBay import HydroponicsBay
from Nodes.LaTeXGenerator import LaTeXGenerator
from Nodes.Node import Node

doc = Document('basic')


generator = LaTeXGenerator()
generator.addNode(HydroponicsBay("hydroponics"))
generator.addNode(Generator("test_generator", label = "Primary generator", custom_description = "This is the main generator!"))
generator.addNode(Generator("test_generator2", label = "Secondary generator", custom_description = "This is the secondary generator"))
generator.fillDocument(doc)

doc.generate_pdf("manual", clean_tex=False)