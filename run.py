from Generator import Generator
from Light import Light
from NodeEngine import NodeEngine
from NodeGraph import NodeGraph
from ResourceStorage import ResourceStorage
from Signal import Signal

engine = NodeEngine()

fuel_tank = ResourceStorage("fuel_tank", "fuel", 1000)
generator = Generator("generator")
fuel_tank.connectWith("fuel", generator)


water_tank = ResourceStorage("water_tank", "water", 750)

water_tank_2 = ResourceStorage("water_tank", "water", 0, 500)
water_tank.connectWith("water", generator)

generator.connectWith("water", water_tank_2)

battery = ResourceStorage("battery", "energy", 10)
battery_2 = ResourceStorage("battery_2", "energy", 0, 15)
generator.connectWith("energy", battery)
generator.connectWith("energy", battery_2)

engine.registerNode(fuel_tank)
engine.registerNode(generator)
engine.registerNode(battery)
engine.registerNode(water_tank)
engine.registerNode(water_tank_2)

'''battery_1 = ResourceStorage("energy", 4)
battery_2 = ResourceStorage("energy", 8)
battery_3 = ResourceStorage("energy", 6)
battery_4 = ResourceStorage("energy", 8)

light_1 = Light("Light 1")
light_2 = Light("Light 2")
light_3 = Light("Light3")

battery_1.connectWith("energy", light_1)

battery_2.connectWith("energy", light_1)
battery_2.connectWith("energy", light_2)

battery_3.connectWith("energy", light_2)
battery_3.connectWith("energy", light_3)

battery_4.connectWith("energy", light_3)



engine.registerNode(light_1)
engine.registerNode(light_2)
engine.registerNode(light_3)

engine.registerNode(battery_1)
engine.registerNode(battery_2)
engine.registerNode(battery_3)
engine.registerNode(battery_4)'''
graph = NodeGraph(generator)
graph_2 = NodeGraph(water_tank)

for _ in range(0, 150):
    engine.doTick()

graph.showGraph()

print("done")

