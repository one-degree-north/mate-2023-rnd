from mcu_interface import MCUInterface
from server import OPiServer
from thruster_control import ThrusterController
from data import OpiDataProcess

if __name__ == "__main__":
    # there is a circular dependency with: thrust_controller requiring data and interface, server requiring thrust_controller, and data requiring server
    # addr = input("server address> ")
    # serial_port = input("serial port > ")
    addr = "192.168.13.103"
    serial_port = "/dev/ttyS5"
    thrust_controller = ThrusterController()
    server = OPiServer((addr, 7772))
    opi_data = OpiDataProcess(server)
    interface = MCUInterface(serial_port)
    # resolve dependencies
    thrust_controller.set_interface(interface)
    thrust_controller.set_data(opi_data)
    server.set_thruster_control(thrust_controller)
    server.set_interface(interface)
    opi_data.set_server(server)
    interface.set_server(server)
    #start stuff!
    print("starting server")
    server.start_server()
    print("starting interface")
    interface.start()
    print("starting BNO")
    opi_data.start_bno_reading()