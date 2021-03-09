import abc
import logging
from typing import Dict
from random import randint

class Cable():

    def __init__(self):
        self.onValueChangedActions = []
        self.value = 0

    def add_action(self, action):
        self.onValueChangedActions += [action]
    
    def get_value(self):
        return self.value

    def set_value(self, val, device):
        self.value = val
        for action in self.onValueChangedActions:
            action(device)


class Device(metaclass=abc.ABCMeta):
    def __init__(self, name: str, ports: Dict[str, Cable]):
        self.name = name
        self.ports = ports

    def port_name(self, port):
        return f'{self.name}_{port}'

    def update(self, time):
        pass

    def connect(self, cable, port_name):
        pass

    def log(self, time, msg):
        logging.info(f'{time} {self.name} {msg}')


class Hub(Device):

    def __init__(self, name, ports_count):
        self.current_transmitting_port = None
        ports = {}
        for i in range(ports_count):
            ports[f'{name}_{i+1}'] = None

        super().__init__(name, ports)

    def retransmit(self, from_port):
        val = self.ports[from_port].value

        if self.current_transmitting_port is None:
            self.current_transmitting_port = from_port
        elif self.current_transmitting_port != from_port:
            val |= self.ports[self.current_transmitting_port]

        for port, cable in self.ports.items():
            if cable is not None:
                cable.set_value(val, self)

    def update(self, time):
        pass

    def connect(self, cable: Cable, port_name: str):

        if self.ports[port_name] is not None:
            raise ValueError(f'Port {port_name} is currently in use.')
        
        self.ports[port_name] = cable

        def action(device):
            if device != self and device is not None:
                self.retransmit(port_name)

        cable.add_action(action)

class PC(Device):
    def __init__(self, name, signal_time):
        ports = { f'{name}_1' : None }
        super().__init__(name, ports)
        self.data = []
        self.current_package = []
        self.package_index = 0
        self.time_to_send = 0
        self.max_time_to_send = 1
        self.signal_time = signal_time
        self.send_time = 0
        self.sending_bit = None
        self.logs = []

    def readjust_max_time_to_send(self):
        self.max_time_to_send *= 2

    @property
    def is_sending(self):
        return self.sending_bit is not None

    @property
    def cable(self):
        return self.ports[self.port_name(1)]

    def load_package(self):
        if self.data and not self.current_package:
            self.current_package = self.data[:8]
            self.data = self.data[8:]
            self.max_time_to_send = 1
            self.package_index = 0
            self.send_time = 0

    def update(self, time):
        self.load_package()

        if self.time_to_send:
            self.log(time, 'waiting for sending')
            self.time_to_send -= 1
            return
        
        if self.current_package:
            self.sending_bit = self.current_package[self.package_index]
            self.cable.set_value(self.sending_bit, self)

            if self.cable.value != self.sending_bit: #collision
                self.log(time, 'collision')
                self.readjust_max_time_to_send()
                self.time_to_send = randint(0, self.max_time_to_send)
                self.package_index = 0
            else:
                if self.send_time == 0:                
                    self.log(time, f'send {self.sending_bit}')
                self.send_time += 1
                if self.send_time == self.signal_time:
                    self.package_index += 1
                    if self.package_index == len(self.current_package):
                        self.current_package = []
                    self.send_time = 0
        
        if not self.current_package:
            self.sending_bit = None
        
        if time % self.signal_time == 0 and not self.is_sending:
            self.log(time, f'recieve {self.cable.value}')
            

    def send(self, data):
        self.data += data

    def connect(self, cable: Cable, port_name: str):

        if self.cable is not None:
            raise ValueError(f'Port {port_name} is currently in use.')

        self.ports[self.port_name(1)] = cable

        def action(device):            
            if self.sending_bit is not None and \
               device is not None and \
               device != self:
                val = self.sending_bit | self.cable.value
                self.cable.set_value(val, None)

        self.cable.add_action(action)

