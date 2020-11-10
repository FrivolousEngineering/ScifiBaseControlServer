from Server.NodeNamespace import node_namespace
from Server.Server import Server

from zeroconf import IPVersion, ServiceInfo, Zeroconf
from Server.Blueprint import blueprint, api
from Server.ControllerNamespace import control_namespace

app = Server()


api.add_namespace(node_namespace)
api.add_namespace(control_namespace)
app.register_blueprint(blueprint)



import sys
import signal
import socket


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
  addresses=[socket.inet_aton(get_ip())],
  port=80,
  properties=desc,
  server="",
)


def handler(signal, frame):
  print("CTRL-C pressed!")
  zeroconf.unregister_service(info)
  zeroconf.close()
  sys.exit(0)


zeroconf = Zeroconf(ip_version=IPVersion.All)
zeroconf.register_service(info)

signal.signal(signal.SIGINT, handler)
app.run(debug=True, host="0.0.0.0")