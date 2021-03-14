import abc
import logging
from functools import reduce
from typing import Dict
from random import randint, seed

seed(0)

class Cable():
    """
    Representa un cable físico.

    Attributes
    ----------
    value : int
        Valor del bit que se transmite.
    """

    def __init__(self):
        self.value = 0


class Device(metaclass=abc.ABCMeta):
    """
    Representa un dispositivo.

    Parameters
    ----------
    name : str
        Nombre del dispositivo.
    ports : Dict[str, Cable]
        Puertos del dispositivo.

        Cada puerto está asociado a un cable. Si para un puerto dado el
        cable asociado es ```None`` significa que este puerto no tiene ningún
        cable conectado.    
    """

    def __init__(self, name: str, ports: Dict[str, Cable]):
        self.name = name
        self.ports = ports
        self.logs = []

    def port_name(self, port: int):
        """
        Devuelve el nombre de un puerto dado su número.

        Parameters
        ----------
        port : int
            Número del puerto.

            Este valor debe ser mayor o igual a 1 y menor o igual que la
            cantidad total de puertos del dispositivo.
        """
        return f'{self.name}_{port}'

    def reset(self):
        """
        Función que se ejecuta al inicio de cada ciclo de simulación para cada
        dispositivo.
        """

    @abc.abstractmethod
    def update(self, time: int):
        """
        Función que se ejecuta en el ciclo de la simulación por cada
        dispositivo.

        Parameters
        ----------
        time : int
            Timepo de ejecución de la simulación.
        """

    @abc.abstractmethod
    def connect(self, cable: Cable, port_name: str):
        """
        Conecta un cable dado a un puerto determinado.

        Parameters
        ----------
        cable : Cable
            Cable a conectar.
        port_name : str
            Nombre del puerto en el que será conectado el cable.
        """

    def log(self, time: int, msg: str, info: str):
        """
        Log
        """
        log_msg = f'| {time: ^10} | {self.name: ^8} | {msg: ^10} | {info: <30} |'
        self.logs.append(log_msg)
        logging.info(log_msg)

    def save_log(self, path=''):
        with open(path + f'{self.name}.txt', 'w+') as file:
            header = f'| {"Time (ms)": ^10} | {"Port":^8} | {"Action" :^10} | {"Info": ^30} |'
            file.write(f'{"-" * len(header)}\n')
            file.write(f'{header}\n')
            file.write(f'{"-" * len(header)}\n')
            file.write('\n'.join(self.logs))
            file.write(f'{"-" * len(header)}\n')

class Hub(Device):

    def __init__(self, name, ports_count):
        self.current_transmitting_port = None
        self.updating = False
        self.received, self.sended = [] , []
        ports = {}
        for i in range(ports_count):
            ports[f'{name}_{i+1}'] = None

        super().__init__(name, ports)

    def reset(self):
        self.updating = False
        for _, cable in self.ports.items():
            if cable is not None:
                cable.value = 0
    
    def save_log(self, path=''):
        with open(path + f'{self.name}.txt', 'w+') as file:
            header = f'| {"Time (ms)": ^10} |'
            for port in self.ports.keys():
                header += f' {port: ^11} |'
            header_len = len(header)
            header += f'\n| {"": ^10} |'
            for port in self.ports.keys():
                header += f' {"Rece . Sent": ^11} |'
            file.write(f'{"-" * header_len}\n')
            file.write(f'{header}\n')
            file.write(f'{"-" * header_len}\n')
            file.write('\n'.join(self.logs))
            file.write(f'\n{"-" * header_len}\n')

    def special_log(self, time, received, sended):
        log_msg = f'| {time: ^10} |'
        for re, se in zip(received, sended):
            if re == '-':
                log_msg += f' {"---" : ^11} |'
            else:
                log_msg += f' {re :>4} . {se: <4} |'
        if self.updating:
            self.logs[-1] = log_msg
        else:
            self.logs.append(log_msg)

    def get_port_value(self, port_name):
        cable = self.ports[port_name]
        return str(cable.value) if cable is not None else '-'

    def update(self, time):
        val = reduce(lambda x, y: x|y, \
        [c.value for c in self.ports.values() if c is not None])

        if not self.updating:
            self.received = [self.get_port_value(p) for p in self.ports.keys()]        

        for _, cable in self.ports.items():
            if cable is not None:
                cable.value = val

        self.sended = [self.get_port_value(p) for p in self.ports.keys()]
        self.special_log(time, self.received, self.sended)
        self.updating = True

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
                self.cable.value = 0


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
            self.cable.value = self.sending_bit

            coll = self.check_collision()

            if not coll:
                if self.send_time == 0:                
                    self.log(self.sim_time, 'Sent', f'{self.sending_bit}')
                self.send_time += 1
                if self.send_time == self.signal_time:
                    self.package_index += 1
                    if self.package_index == len(self.current_package):
                        self.current_package = []              
                    self.send_time = 0

        self.time_connected += 1

    def send(self, data):
        self.data += data

    def receive(self):
        if self.is_sending:
            self.check_collision()
        elif self.time_connected % self.signal_time == 0 and \
           not self.is_sending:
            self.log(self.sim_time, 'Received', f'{self.cable.value}')

    def check_collision(self):
        if self.is_sending and self.cable.value != self.sending_bit: #collision
            self.readjust_max_time_to_send()
            self.time_to_send = randint(0, self.max_time_to_send)
            self.log(self.sim_time, 'Collision', f'Waitting {self.time_to_send}ms to send')
            self.package_index = 0
            self.send_time = 0
            self.is_sending = False
            return True
        return False

    def connect(self, cable: Cable, port_name: str):

        if self.cable is not None:
            raise ValueError(f'Port {port_name} is currently in use.')

        self.ports[self.port_name(1)] = cable
