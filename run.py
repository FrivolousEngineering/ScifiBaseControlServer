from Generator import Generator
from Light import Light
from NodeEngine import NodeEngine
from NodeGraph import NodeGraph
from ResourceStorage import ResourceStorage
from Signal import Signal
from FluidCooler import FluidCooler
engine = NodeEngine()

fuel_tank = ResourceStorage("fuel_tank", "fuel", 1000)
generator = Generator("generator")
fuel_tank.connectWith("fuel", generator)
fluid_cooler = FluidCooler("fluid_cooler", "water", 10)
fluid_cooler_2 = FluidCooler("fluid_cooler", "water", 10)

water_tank = ResourceStorage("water_tank", "water", 750)


water_tank.connectWith("water", generator)

generator.connectWith("water", fluid_cooler)
fluid_cooler.connectWith("water", fluid_cooler_2)
fluid_cooler_2.connectWith("water", water_tank)

battery = ResourceStorage("battery", "energy", 10)
battery_2 = ResourceStorage("battery_2", "energy", 0, 15)
generator.connectWith("energy", battery)
generator.connectWith("energy", battery_2)

engine.registerNode(fuel_tank)
engine.registerNode(generator)
engine.registerNode(battery)
engine.registerNode(water_tank)
engine.registerNode(fluid_cooler)
engine.registerNode(fluid_cooler_2)

graph = NodeGraph(generator)
graph_2 = NodeGraph(fluid_cooler)
graph_3 = NodeGraph(fluid_cooler_2)
graph_4 = NodeGraph(water_tank)

for _ in range(0, 80):
    engine.doTick()

graph.showGraph()
graph_2.showGraph()
graph_3.showGraph()
graph_4.showGraph()

print("done")

