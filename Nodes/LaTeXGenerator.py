from collections import defaultdict
import matplotlib
from pylatex import Section, Subsection, Tabular, LineBreak, NewLine, Figure, Subsubsection
from pylatex.utils import italic, bold, NoEscape

matplotlib.use('Agg')  # Not to use X server. For TravisCI.
import matplotlib.pyplot as plt  # noqa

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

    temperature_specific_properties = ["optimal_temperature", "optimal_temperature_range"]

    def __init__(self) -> None:
        self._nodes = defaultdict(list)

    def addNode(self, node):
        self._nodes[type(node)].append(node)
        node.ensureSaneValues()

    def fillDocument(self, doc):
        for node_type, nodes in self._nodes.items():
            with doc.create(Section(self._convertPropertyToHumanReadable(node_type.__name__))):
                doc.append(nodes[0].description)

                for node in nodes:
                    with doc.create(Subsection(self._convertPropertyToHumanReadable(node.label))):
                        doc.append(node.custom_description)
                        doc.append(NewLine())
                        doc.append(NewLine())
                        self._generateStatTable(doc, node)
                        self._generateRequiredResourceTable(doc, node)
                        self._generateOptionalResourceTable(doc, node)

                        self._generateTemperatureEfficiencyGraph(doc, node)

                        self._generateHealthEffectivenessGraph(doc, node)

    def _generateHealthEffectivenessGraph(self, doc, node):
        with doc.create(Subsubsection("Health Effectiveness")):
            doc.append("Damage has the following effect on the node")
            doc.append(NewLine())

            healths = list(range(0, 100))
            effectiveness_factors = []

            for health in healths:
                node._health = health
                effectiveness_factors.append(node._getHealthEffectivenessFactor())

            plt.plot(healths, effectiveness_factors)
            with doc.create(Figure(position='H')) as plot:
                plot.add_plot(width = NoEscape(r'0.5\textwidth'))
            plt.close()

    def _generateTemperatureEfficiencyGraph(self, doc, node):
        with doc.create(Subsubsection("Temperature Effectiveness")):
            doc.append("Temperature has the following effect on the node")
            doc.append(NewLine())
            optimal_temperature = node.optimal_temperature
            temperature_range = node.optimal_temperature_range

            temperatures = list(range(int(optimal_temperature - 1.2 * temperature_range), int(optimal_temperature + 1.2 * temperature_range)))

            effectiveness_factors = []
            original_temp = node._temperature
            for temperature in temperatures:
                node._temperature = temperature
                effectiveness_factors.append(node.effectiveness_factor)

            plt.plot(temperatures, effectiveness_factors)
            with doc.create(Figure(position='H')) as plot:
                plot.add_plot(width = NoEscape(r'0.5\textwidth'))
            plt.close()
            node._temperature = original_temp

    def _convertPropertyToHumanReadable(self, property_name: str) -> str:
        result = property_name.replace("_", " ")
        result = result.capitalize()
        return result

    def _generateRequiredResourceTable(self, doc, node):
        with doc.create(Subsubsection("Required Resources")):
            doc.append("It requires the following resources to function correctly")

            if not node._original_resources_required_per_tick:
                return

            doc.append(NewLine())
            doc.append(NewLine())

            with doc.create(Tabular(' l | r ')) as table:
                table.add_row(["Resource", "Value"], mapper=[bold])
                for resource_type, resource_value in node._original_resources_required_per_tick.items():
                    table.add_hline()
                    table.add_row((self._convertPropertyToHumanReadable(resource_type), resource_value))


    def _generateOptionalResourceTable(self, doc, node):
        with doc.create(Subsubsection("Optional Resources")):
            doc.append("It can accept the following optional resources")

            if not node._original_optional_resources_required_per_tick:
                return

            doc.append(NewLine())
            doc.append(NewLine())
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
