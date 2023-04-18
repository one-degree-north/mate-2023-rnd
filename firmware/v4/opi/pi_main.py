from mcu_interface import MCUInterface
from server import OPiServer
from thruster_control import ThrusterController
from data import OpiDataProcess
import threading
import json

if __name__ == "__main__":
    # setup configuration file contents
    config_file = open('config.json', 'r')
    config = json.loads(config_file.read())
    config_file.close()

    # create components
    addr = config['ip_addr']
    serial_port = config['serial_port']
    thrust_controller = ThrusterController(config['thruster_move_delta'], not not config['debug'])
    server = OPiServer((addr, config['udp_port']))
    interface = MCUInterface(serial_port)

    # resolve dependencies between components
    thrust_controller.set_interface(interface)
    server.set_thruster_control(thrust_controller)
    server.set_interface(interface)
    interface.set_server(server)

    # config if we are using bno data
    if config['use_bno']:
        opi_data = OpiDataProcess()
        thrust_controller.set_data(opi_data)
        opi_data.set_server(server)

    # start the system
    print("starting server")
    server.start_server()
    print("starting interface")
    interface.start()
    if config['use_bno']:
        print("starting BNO")
        opi_data.start_bno_reading()
    print("starting thruster controller")
    thrust_controller.start_loop()
    server.server_thread.join()
