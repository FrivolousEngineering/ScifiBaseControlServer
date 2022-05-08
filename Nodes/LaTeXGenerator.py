from collections import defaultdict

from pylatex import Section, Subsection, Tabular, LineBreak, NewLine
from pylatex.utils import italic, bold


class LaTeXGenerator:

    propertiesToAdd = ["weight",
                       "performance_change_factor",
                       "min_performance",
                       "max_performance",
                       "heat_emissivity",
                       "surface_area",
                       "heat_convection_coefficient",
                       "max_safe_temperature",
                       "max_health",
                       ]

    def __init__(self) -> None:
        self._nodes = defaultdict(list)

    def addNode(self, node):
        self._nodes[type(node)].append(node)
        node.ensureSaneValues()

    def fillDocument(self, doc):
        for node_type, nodes in self._nodes.items():
            with doc.create(Section(node_type.__name__)):
                doc.append(nodes[0].description)

                for node in nodes:
                    with doc.create(Subsection(node.label)):
                        doc.append(node.custom_description)
                        doc.append(NewLine())
                        doc.append(NewLine())
                        self._generateStatTable(doc, node)
                        doc.append(NewLine())
                        doc.append(NewLine())
                        doc.append("It requires the following resources to function correctly")
                        doc.append(NewLine())
                        doc.append(NewLine())
                        self._generateRequiredResourceTable(doc, node)

                        doc.append(NewLine())
                        doc.append(NewLine())
                        doc.append("It requires the following optional resources")
                        doc.append(NewLine())
                        doc.append(NewLine())
                        self._generateOptionalResourceTable(doc, node)


    def _convertPropertyToHumanReadable(self, property_name: str) -> str:
        result = property_name.replace("_", " ")
        result = result.capitalize()
        return result

    def _generateRequiredResourceTable(self, doc, node):
        with doc.create(Tabular(' l | r ')) as table:
            table.add_row(["Resource", "Value"], mapper=[bold])
            for resource_type, resource_value in node._original_resources_required_per_tick.items():
                table.add_hline()
                table.add_row((self._convertPropertyToHumanReadable(resource_type), resource_value))


    def _generateOptionalResourceTable(self, doc, node):
        with doc.create(Tabular(' l | r ')) as table:
            table.add_row(["Resource", "Value"], mapper=[bold])
            for resource_type, resource_value in node._original_optional_resources_required_per_tick.items():
                table.add_hline()
                table.add_row((self._convertPropertyToHumanReadable(resource_type), resource_value))


    def _generateStatTable(self, doc, node):
        with doc.create(Tabular(' l | r ')) as table:
            table.add_row(["Property", "Value"], mapper = [bold])
            for item in self.propertiesToAdd:
                table.add_hline()
                table.add_row((self._convertPropertyToHumanReadable(item), getattr(node, item)))
