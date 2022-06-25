from collections import defaultdict
import matplotlib
from pylatex import Section, Subsection, Tabular, LineBreak, NewLine, Figure, Subsubsection, Hyperref, Marker
from pylatex.utils import italic, bold, NoEscape
import re

matplotlib.use('Agg')  # Not to use X server. For TravisCI.
import matplotlib.pyplot as plt  # noqa


class LaTeXGenerator:
    propertiesToAdd = ["weight",
                       "heat_emissivity",
                       "surface_area",
                       "heat_convection_coefficient",
                       "max_safe_temperature",
                       "max_health"
                       ]

    performance_properties = ["performance_change_factor", "min_performance", "max_performance"]

    temperature_specific_properties = ["optimal_temperature", "optimal_temperature_range"]

    def __init__(self) -> None:
        self._nodes = defaultdict(list) # type: ignore

    def addNode(self, node):
        self._nodes[type(node)].append(node)
        node.ensureSaneValues()

    def fillDocument(self, doc):
        with doc.create(Section("Properties")):
            doc.append("This chapter explains the various properties listed by the various devices.")
            with doc.create(Subsection("Weight")):
                doc.append("The weight of the device in kilogram. Note that this value can fluctuate. Storages will also include the weight of their stored resources as part of their own weight. This means that an empty storage tank will heat up significantly faster")
            with doc.create(Subsection("Heat Emissivity")):
                doc.append("How well does this device emit heat by means of radiation? This includes both visible radiation by means of light, but in most cases only includes infrared radiation. The ratio varies from 0 to 1. The surface of a perfect black body (with an emissivity of 1) emits thermal radiation at the rate of approximately 448 watts per square metre at room temperature (25 °C, 298.15 K); all real objects have emissivities less than 1.0, and emit radiation at correspondingly lower rates.")
            with doc.create(Subsection("Surface Area")):
                doc.append("What is the surface area of this device in m2. Larger numbers indicate that much more heat can be emitted by means of (infrared) emission, but also by means of heat convection.")
            with doc.create(Subsection("Heat Convection Coefficient")):
                doc.append("How well is this device insulated? All values are reported in W/m K. Steel objects tend to be in the 16-24 range, aluminum is well above the 200 range, whereas most plastic is below the 0.25 range")
            with doc.create(Subsection("Max Safe Temperature")):
                doc.append("The maximum temperature (in Kelvin) that this device should be operated at. The further it goes above this number, the faster it will start to receive damage. It is strongly advised to keep all devices well below this temperature to ensure a continued operation.")
            with doc.create(Subsection("Performance Change Factor")):
                doc.append("How quickly is this device able to react to requested changes from engineers? If the factor is one, the device is able to change is current performance to the target performance directly. The higher this number, the slower it is to react to changes.")


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

                        self._generateOutgoingConnectionList(doc, node)

                        self._generateIncomingConnectionsList(doc, node)

    def _generateOutgoingConnectionList(self, doc, node):
        outgoing_connections = node.getAllOutgoingConnections()

        with doc.create(Subsubsection("Outgoing Connections")):
            if not outgoing_connections:
                doc.append("No outgoing connections")
                return
            with doc.create(Tabular(' l | r ')) as table:
                table.add_row(["Target", "Resource"], mapper=[bold])
                for connection in outgoing_connections:

                    sanitized_label = self._convertPropertyToHumanReadable(connection.target.label)
                    table.add_hline()
                    table.add_row((Hyperref(Marker(sanitized_label, "subsec"), sanitized_label)), connection.resource_type.title())

    def _generateIncomingConnectionsList(self, doc, node):
        incoming_connections = node.getAllIncomingConnections()

        with doc.create(Subsubsection("Incoming Connections")):
            if not incoming_connections:
                doc.append("No incoming connections")
                return
            with doc.create(Tabular(' l | r ')) as table:
                table.add_row(["Target", "Resource"], mapper=[bold])
                for connection in incoming_connections:
                    sanitized_label = self._convertPropertyToHumanReadable(connection.origin.label)
                    table.add_hline()
                    table.add_row((Hyperref(Marker(sanitized_label, "subsec"), sanitized_label)),
                                  connection.resource_type.title())

    def _generateHealthEffectivenessGraph(self, doc, node):
        with doc.create(Subsubsection("Health Effectiveness")):
            doc.append("Damage has the following effect on the device")
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
            doc.append("Temperature has the following effect on the device")
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
        # Add spaces in front of capitals
        property_name = re.sub(r"(\w)([A-Z])", r"\1 \2", property_name)
        result = property_name.replace("_", " ")
        result = result.title()
        return result

    def _generateRequiredResourceTable(self, doc, node):
        with doc.create(Subsubsection("Required Resources")):
            if not node._original_resources_required_per_tick.items():
                doc.append("It requires no resources to function correctly")
            else:
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
            if node._original_optional_resources_required_per_tick.items():
                doc.append("It can accept the following optional resources")
            else:
                doc.append("It doesn't need any optional resources")

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

            if node.isTemperatureDependant:
                for item in self.temperature_specific_properties:
                    table.add_hline()
                    table.add_row((self._convertPropertyToHumanReadable(item), getattr(node, item)))

            if node.hasSettablePerformance:
                for item in self.performance_properties:
                    table.add_hline()
                    table.add_row((self._convertPropertyToHumanReadable(item), getattr(node, item)))

            if hasattr(node, "max_amount_stored") and getattr(node, "max_amount_stored") != -1:
                table.add_hline()
                table.add_row((self._convertPropertyToHumanReadable("Max amount stored"), getattr(node, "max_amount_stored")))
            if hasattr(node, "_resource_type"):
                table.add_hline()
                table.add_row((self._convertPropertyToHumanReadable("Resource type"), getattr(node, "_resource_type")))
            if hasattr(node, "max_resources_per_tick"):
                table.add_hline()
                table.add_row(
                    (self._convertPropertyToHumanReadable("Resource Flow"), getattr(node, "max_resources_per_tick")))


