from mcu_interface import MCUInterface
from server import OPiServer
from thruster_control import ThrusterController
from data import OpiDataProcess

if __name__ == "__main__":
    # there is a circular dependency with: thrust_controller requiring data and interface, server requiring thrust_controller, and data requiring server
    thrust_controller = ThrusterController()
    server = OPiServer((input("server address> ")), thrust_controller)
    opi_data = OpiDataProcess(server)
    interface = MCUInterface(input("serial port > "), server)
    # resolve dependencies
    thrust_controller.set_interface(interface)
    thrust_controller.set_data(opi_data)
    server.set_thruster_control(thrust_controller)
    server.set_interface(interface)
    opi_data.set_server(server)
    interface.set_server(server)
    #start stuff!
    server.start_server()
    interface.start()
    opi_data.start_bno_reading()