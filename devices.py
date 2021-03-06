import abc
import logging

EMPTY = -1
CERO = 0
ONE = 1

class Port():
    def __init__(self, name):
        self.name = name

class Cable():

    def __init__(self, port1, port2):
        self.port1 = port1
        self.port2 = port2
        self.value = EMPTY


class Device(metaclass=abc.ABCMeta):
    def __init__(self, ports, signal_time, max_chunck=8):
        self.ports = ports

        self.signal_time = signal_time

        self.rest_time = 0
        self.sending_time = 0

        self.data = []
        self.is_sending = False

        self.max_chunck = max_chunck
        self.sending_chunkc = 0

    def update(self):
        pass
    
    def write(self, data):
        self.data += data

    def read(self):
        out = []
        for cable in ports.values():
            if not cable or cable.value == EMPTY:
                out.append(None)
            else:
                out.append(cable.value)
        return out

class Hub(Device):

    def __init__(self, name, ports_count):
        if ports_count != 4 and
           ports_count != 8:
           raise ValueError('Hubs can take only 4 or 8 ports')

        ports = {}
        for i in range(ports_count):
            ports[f'{name}_{i}'] = None

    def write(self, data):
