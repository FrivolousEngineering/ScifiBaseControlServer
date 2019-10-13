from Generator import Generator
from Light import Light
from NodeEngine import NodeEngine
from ResourceStorage import ResourceStorage

engine = NodeEngine()

fuel_tank = ResourceStorage("fuel", 20)
generator = Generator()
fuel_tank.connectWith("fuel", generator)

battery = ResourceStorage("energy", 10, 11)
battery_2 = ResourceStorage("energy", 0, 15)
generator.connectWith("energy", battery)
generator.connectWith("energy", battery_2)

engine.registerNode(fuel_tank)
engine.registerNode(generator)
engine.registerNode(battery)

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


engine.doTick()

