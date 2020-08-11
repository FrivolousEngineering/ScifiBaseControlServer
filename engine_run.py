from Nodes.Modifiers.OverrideDefaultSafetyControlsModifier import OverrideDefaultSafetyControlsModifier
from Nodes.NodeEngine import NodeEngine
import json

from Nodes.DBusService import DBusService

import dbus.mainloop.glib
from gi.repository import GLib

from Nodes.TemperatureHandlers.RandomFluctuatingTemperatureHandler import RandomFluctuatingTemperatureHandler

engine = NodeEngine()

with open("configuration.json") as f:
    loaded_data = json.loads(f.read())
    engine.registerNodesFromConfigurationData(loaded_data["nodes"])
    engine.registerConnectionsFromConfigurationData(loaded_data["connections"])

    # Add a random temperature fluctuation
    engine.setOutsideTemperatureHandler(RandomFluctuatingTemperatureHandler())

generator = engine.getNodeById("generator_1")
generator.addModifier(OverrideDefaultSafetyControlsModifier(5))
engine.doTick()
#storage = NodeStorage(engine)

#engine.start()

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

loop = GLib.MainLoop()
object = DBusService(engine)
loop.run()


print("done")
