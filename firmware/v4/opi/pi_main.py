from mcu_interface import MCUInterface
from server import OPiServer
from thruster_control import ThrusterController
from data import OpiDataProcess
import threading
import yappi
import time
import json


def main(stop_event):
    # setup configuration file contents
    config_file = open('config.json', 'r')
    config = json.loads(config_file.read())
    config_file.close()

    # create components
    addr = config['ip_addr']
    serial_port = config['serial_port']
    thrust_controller = ThrusterController(config['thruster_move_delta'], stop_event, not not config['debug'])
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
    
    return thrust_controller, server, opi_data, interface

if __name__ == "__main__":
    yappi.start()
    stop_event = threading.Event()
    thrust_controller, server, opi_data, interface = main(stop_event)
    time.sleep(86400) # kill after 1 day (why would it even run that long?)
    stop_event.set()
    server.server_thread.join()
    yappi.stop()

    # retrieve thread stats by their thread id (given by yappi)
    threads = yappi.get_thread_stats()
    for thread in threads:
        print(
            "Function stats for (%s) (%d)" % (thread.name, thread.id)
        )  # it is the Thread.__class__.__name__
        yappi.get_func_stats(ctx_id=thread.id).print_all()
