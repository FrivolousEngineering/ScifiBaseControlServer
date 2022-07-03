import json

from pylatex import Document, Package


from Nodes.LaTeXGenerator import LaTeXGenerator
from Nodes.NodeEngine import NodeEngine

doc = Document('basic')
doc.packages.append(Package('float'))

generator = LaTeXGenerator()
engine = NodeEngine()

with open("configuration.json") as f:
    loaded_data = json.loads(f.read())
    engine.deserialize(loaded_data)

for node in engine.getAllNodes().values():
    generator.addNode(node)

generator.fillDocument(doc)

doc.generate_pdf("manual", clean_tex = False)
