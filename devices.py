import abc
import logging
from functools import reduce
from typing import Dict
from random import randint, seed

CERO = 0
ONE = 1

seed(0)

class Cable():

    def __init__(self):
        self.value = CERO
    
    def get_value(self):
        return self.value

    def set_value(self, val):
        self.value = val


class Device(metaclass=abc.ABCMeta):
    def __init__(self, name: str, ports: Dict[str, Cable]):
        self.name = name
        self.ports = ports
        self.logs = []

    def port_name(self, port):
        return f'{self.name}_{port}'

    def reset(self):
        pass

    def update(self, time):
        pass

    def connect(self, cable, port_name):
        pass

    def log(self, time, msg):
        log_msg = f'{time} {self.name} {msg}'
        self.logs.append(log_msg)
        logging.info(log_msg)

    def save_log(self, path=''):
        with open(path + f'{self.name}.txt', 'w+') as f:
            f.write('\n'.join(self.logs))

class Hub(Device):

    def __init__(self, name, ports_count):
        self.current_transmitting_port = None
        ports = {}
        for i in range(ports_count):
            ports[f'{name}_{i+1}'] = None

        super().__init__(name, ports)

    def reset(self):
        for _, cable in self.ports.items():
            if cable is not None:
                cable.set_value(0)

    def update(self, time):
        val = reduce(lambda x, y: x|y, \
        [c.value for c in self.ports.values() if c is not None])

        for _, cable in self.ports.items():
            if cable is not None:
                cable.set_value(val)

    def connect(self, cable: Cable, port_name: str):

        if self.ports[port_name] is not None:
            raise ValueError(f'Port {port_name} is currently in use.')
        
        self.ports[port_name] = cable

class PC(Device):
    def __init__(self, name, signal_time):
        ports = {f'{name}_1' : None}
        super().__init__(name, ports)
        self.data = []
        self.current_package = []
        self.package_index = 0
        self.time_to_send = 0
        self.max_time_to_send = 1
        self.signal_time = signal_time
        self.send_time = 0
        self.sending_bit = 0
        self.is_sending = False
        self.logs = []
        self.time_connected = 0
        self.sim_time = 0

    def readjust_max_time_to_send(self):
        self.max_time_to_send *= 2

    @property
    def cable(self):
        return self.ports[self.port_name(1)]

    def load_package(self):
        if not self.current_package:
            if self.data:
                self.current_package = self.data[:8]
                self.data = self.data[8:]
                self.max_time_to_send = 8
                self.package_index = 0
                self.send_time = 0
                self.is_sending = True
            elif self.is_sending:
                self.sending_bit = 0
                self.is_sending = False
                self.cable.set_value(0)


    def update(self, time):
        self.sim_time = time
        self.load_package()

        if self.time_to_send:
            self.time_to_send -= 1

        if self.time_to_send:
            return
        
        if self.current_package:
            self.is_sending = True
            self.sending_bit = self.current_package[self.package_index]
            # self.log(time, f'Trying to send {self.sending_bit}')
            self.cable.set_value(self.sending_bit)

            coll = self.check_collision()

            if not coll:
                if self.send_time == 0:                
                    self.log(self.sim_time, f'send {self.sending_bit}')
                self.send_time += 1
                if self.send_time == self.signal_time:
                    self.package_index += 1
                    if self.package_index == len(self.current_package):
                        self.current_package = []              
                    self.send_time = 0

        self.time_connected += 1

    def send(self, data):
        self.data += data

    def recieve(self):
        if self.is_sending:
            self.check_collision()
        elif self.time_connected % self.signal_time == 0 and \
           not self.is_sending:
            self.log(self.sim_time, f'recieve {self.cable.value}')

    def check_collision(self):
        if self.is_sending and self.cable.value != self.sending_bit: #collision
            self.readjust_max_time_to_send()
            self.time_to_send = randint(0, self.max_time_to_send)
            self.log(self.sim_time, f'Collision, waitting {self.time_to_send}ms to send')
            self.package_index = 0
            self.send_time = 0
            self.is_sending = False
            return True
        return False

    def connect(self, cable: Cable, port_name: str):

        if self.cable is not None:
            raise ValueError(f'Port {port_name} is currently in use.')

        self.ports[self.port_name(1)] = cable
