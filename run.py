from Generator import Generator
from Light import Light
from ResourceStorage import ResourceStorage


battery_1 = ResourceStorage("energy", 4)
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

light_1.preUpdate()
light_2.preUpdate()
light_3.preUpdate()


def updateReservations():
    battery_1.updateReservations()
    battery_2.updateReservations()
    battery_3.updateReservations()
    battery_4.updateReservations()


updateReservations()
timer = 0
while light_1.requiresReplanning() or light_2.requiresReplanning() or light_3.requiresReplanning():
    print("Replanningg!", light_1.requiresReplanning(), light_2.requiresReplanning(), light_3.requiresReplanning())
    if light_1.requiresReplanning():
        light_1.replanReservations()
    if light_2.requiresReplanning():
        light_2.replanReservations()
    if light_3.requiresReplanning():
        light_3.replanReservations()
    updateReservations()
    print("")


light_1.update()
light_2.update()
light_3.update()

print("Light 1:", light_1.isOn)
print("Light 2:", light_2.isOn)
print("Light 3:", light_3.isOn)
print("Run completed")