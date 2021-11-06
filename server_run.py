from Server.NodeNamespace import node_namespace
from Server.Server import Server

from zeroconf import IPVersion, ServiceInfo, Zeroconf
from Server.Blueprint import blueprint, api
from Server.ControllerNamespace import control_namespace
from Server.ModifierNamespace import modifier_namespace
from Server.RFIDNamespace import RFID_namespace

import sys
import signal
import socket


app = Server()
api.add_namespace(node_namespace)
api.add_namespace(control_namespace)
api.add_namespace(modifier_namespace)
api.add_namespace(RFID_namespace)
app.register_blueprint(blueprint)


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


desc = {}

info = ServiceInfo(
  "_ScifiBase._tcp.local.",
  "Base-Control-Server._ScifiBase._tcp.local.",
  addresses = [socket.inet_aton(get_ip())],
  port = 80,
  properties = desc,
  server = "",
)


def handler(signal, frame):
  print("CTRL-C pressed!")
  zeroconf.unregister_service(info)
  zeroconf.close()
  sys.exit(0)


zeroconf = Zeroconf(ip_version=IPVersion.All)

zeroconf.register_service(info, allow_name_change= True)

signal.signal(signal.SIGINT, handler)
app.run(debug=True, host="0.0.0.0")
