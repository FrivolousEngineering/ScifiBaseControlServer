from Nodes.NodeEngine import NodeEngine
import json

from Nodes.NodeStorage import NodeStorage
from Nodes.DBusService import DBusService

import dbus.mainloop.glib
from gi.repository import GLib

engine = NodeEngine()

with open("configuration.json") as f:
    loaded_data = json.loads(f.read())
    engine.registerNodesFromConfigurationData(loaded_data["nodes"])
    engine.registerConnectionsFromConfigurationData(loaded_data["connections"])


storage = NodeStorage(engine)

for _ in range(0, 150):
    engine.doTick()

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

loop = GLib.MainLoop()
object = DBusService(engine)
loop.run()


print("done")
