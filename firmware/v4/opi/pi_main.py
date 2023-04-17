from mcu_interface import MCUInterface
from server import OPiServer
from thruster_control import ThrusterController
from data import OpiDataProcess
import threading
import yappi
import time


def main(stop_event):
    # there is a circular dependency with: thrust_controller requiring data and interface, server requiring thrust_controller, and data requiring server
    # addr = input("server address> ")
    # serial_port = input("serial port > ")
    addr = "192.168.13.101"
    serial_port = "/dev/ttyS1"
    thrust_controller = ThrusterController(stop_event=stop_event)
    server = OPiServer((addr, 7772),stop_event=stop_event)
    opi_data = OpiDataProcess(stop_event=stop_event)
    interface = MCUInterface(serial_port, stop_event)
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
    print("starting thruster controller")
    thrust_controller.start_loop()
    
    return thrust_controller, server, opi_data, interface

if __name__ == "__main__":
    yappi.start()
    stop_event = threading.Event()
    thrust_controller, server, opi_data, interface = main(stop_event)
    time.sleep(30)
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
