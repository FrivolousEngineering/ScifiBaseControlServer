from Nodes.Modifiers.OverrideDefaultSafetyControlsModifier import OverrideDefaultSafetyControlsModifier
from Nodes.NodeEngine import NodeEngine
import json

from Nodes.DBusService import DBusService

import dbus.mainloop.glib
from gi.repository import GLib

from Nodes.NodeStorage import NodeStorage
from Nodes.TemperatureHandlers.PreScriptedTemperatureHandler import PreScriptedTemperatureHandler
from Nodes.TemperatureHandlers.RandomFluctuatingTemperatureHandler import RandomFluctuatingTemperatureHandler

engine = NodeEngine()

with open("configuration2.json") as f:
    loaded_data = json.loads(f.read())
    engine.deserialize(loaded_data)

    # Add a random temperature fluctuation
    engine.setOutsideTemperatureHandler(PreScriptedTemperatureHandler())

storage = NodeStorage(engine)

#storage.restoreNodeState()

#engine.doTick()


#engine.start()

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

loop = GLib.MainLoop()
object = DBusService(engine)
loop.run()


print("done")
