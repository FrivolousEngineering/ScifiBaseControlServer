from Nodes.NodeEngine import NodeEngine
import json

from Nodes.NodesDBusService import NodesDBusService
from Nodes.Modifiers.ModifiersDBusService import ModifiersDBusService
import dbus.mainloop.glib
from gi.repository import GLib

from Nodes.NodeStorage import NodeStorage
from Nodes.TemperatureHandlers.PreScriptedTemperatureHandler import PreScriptedTemperatureHandler

engine = NodeEngine()

with open("configuration.json") as f:
    loaded_data = json.loads(f.read())
    engine.deserialize(loaded_data)

    # Add a random temperature fluctuation
    engine.setOutsideTemperatureHandler(PreScriptedTemperatureHandler())


#storage = NodeStorage(engine)
#modifier = ModifierFactory.createModifier("OverrideDefaultSafetyControlsModifier")
#engine.getNodeById("generator_1").addModifier(modifier)
#storage.restoreNodeState()

engine.doTick()
engine.start()


#engine.start()

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

loop = GLib.MainLoop()
object = NodesDBusService(engine)
object_2 = ModifiersDBusService()
loop.run()


print("done")
