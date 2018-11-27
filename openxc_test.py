from openxc.interface import UsbVehicleInterface

def receive(message, **kwargs):
    # this callback will receive each message received as a dict
    print(message['name'])

vi = UsbVehicleInterface(callback=receive)
vi.start()
# This will block until the connection dies or you exit the program
vi.join()
