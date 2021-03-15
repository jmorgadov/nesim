import abc
import logging
from functools import reduce
from pathlib import Path
from typing import Dict, List
from random import randint, seed
from collections import Counter

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
        cable asociado es ``None`` significa que este puerto no tiene ningún
        cable conectado.
    
    Attributes
    ----------
    name : str
        Nombre del dispositivo.
    ports : Dict[str, Cable]
        Puertos del dispositivo.

        Cada puerto está asociado a un cable. Si para un puerto dado el
        cable asociado es ```None`` significa que este puerto no tiene ningún
        cable conectado.
    logs : List[str]
        Logs del dispositivo.
    sim_time : int
        Timepo de ejecución de la simulación.

        Este valor se actualiza en cada llamado a la función ``update``.
    """

    def __init__(self, name: str, ports: Dict[str, Cable]):
        self.name = name
        self.ports = ports
        self.logs = []
        self.sim_time = 0

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

    def update(self, time: int):
        """
        Función que se ejecuta en el ciclo de la simulación por cada
        dispositivo.

        Parameters
        ----------
        time : int
            Timepo de ejecución de la simulación.
        """

        self.sim_time = time

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

    def disconnect(self, port_name: str):
        """
        Desconecta un puerto de un dispositivo.

        Parameters
        ----------
        port_name : str
            Nombre del puerto a desconectar.
        """

        self.ports[port_name] = None


    def log(self, time: int, msg: str, info: str = ''):
        """
        Escribe un log en el dispositivo.

        Los logs de cada dispositivo se guardarán en archivos separados
        al finalizar la simulación.

        Parameters
        ----------
        time : int
            Timepo de ejecución de la simulación.
        msg : str
            Mensaje que guardará.
        info : str
            Información adicional.
        """

        log_msg = f'| {time: ^10} | {self.name: ^12} | {msg: ^14} | {info: <30} |'
        self.logs.append(log_msg)
        logging.info(log_msg)

    def save_log(self, path: str = ''):
        """
        Guarda los logs del dispositivo en una ruta dada.

        Parameters
        ----------
        path : str
            Ruta donde se guardarán los logs. (Por defecto en la raíz)
        """
        
        output_folder = Path(path)
        output_folder.mkdir(parents=True, exist_ok=True)        
        output_path = output_folder / Path(f'{self.name}.txt')
        with open(str(output_path), 'w+') as file:
            header = f'| {"Time (ms)": ^10} | {"Device":^12} | {"Action" :^14} | {"Info": ^30} |'
            file.write(f'{"-" * len(header)}\n')
            file.write(f'{header}\n')
            file.write(f'{"-" * len(header)}\n')
            file.write('\n'.join(self.logs))
            file.write(f'\n{"-" * len(header)}\n')

class Hub(Device):
    """
    Representa un Hub en la simulación.

    Parameters
    ----------
    name : str
        Nombre del hub.
    ports_count : int
        Cantidad de puertos del hub.
    """

    def __init__(self, name: str, ports_count: int):
        self.current_transmitting_port = None
        self._updating = False
        self._received, self._sent = [], []
        ports = {}
        for i in range(ports_count):
            ports[f'{name}_{i+1}'] = None

        super().__init__(name, ports)

    def reset(self):
        self._updating = False
        for _, cable in self.ports.items():
            if cable is not None:
                cable.value = 0

    def save_log(self, path=''):
        output_folder = Path(path)
        output_folder.mkdir(parents=True, exist_ok=True)        
        output_path = output_folder / Path(f'{self.name}.txt')
        with open(str(output_path), 'w+') as file:
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

    def special_log(self, time: int, received: List[int], sent: List[int]):
        """
        Representación especial para los logs de los hubs.

        Parameters
        ----------
        time : int
            Timepo de ejecución de la simulación.
        received : List[int]
            Lista de bits recibidos por cada puerto.        
        sent : List[int]
            Lista de bits enviados por cada puerto.
        """

        log_msg = f'| {time: ^10} |'
        for re, se in zip(received, sent):
            if re == '-':
                log_msg += f' {"---" : ^11} |'
            else:
                log_msg += f' {re :>4} . {se: <4} |'
        if self._updating:
            self.logs[-1] = log_msg
        else:
            self.logs.append(log_msg)

    def get_port_value(self, port_name: str):
        """
        Devuelve el valor del cable conectado a un puerto dado. En caso de no
        tener un cable conectado devuelve ``'-'``.

        Parameters
        ----------
        port_name : str
            Nombre del puerto.
        """
        cable = self.ports[port_name]
        return str(cable.value) if cable is not None else '-'

    def update(self, time):
        super().update(time)
        val = reduce(lambda x, y: x|y, \
        [c.value for c in self.ports.values() if c is not None])

        if not self._updating:
            self._received = [self.get_port_value(p) for p in self.ports.keys()]        

        for _, cable in self.ports.items():
            if cable is not None:
                cable.value = val

        self._sent = [self.get_port_value(p) for p in self.ports.keys()]
        self.special_log(time, self._received, self._sent)
        self._updating = True

    def connect(self, cable: Cable, port_name: str):
        if self.ports[port_name] is not None:
            raise ValueError(f'Port {port_name} is currently in use.')

        self.ports[port_name] = cable

    def disconnect(self, port_name: str):
        return super().disconnect(port_name)


class PC(Device):
    """
    Representa una PC (Host).

    Parameters
    ----------
    name : str
        Nombre de la PC.
    signal_time : int
        Tiempo mínimo que debe estar un bit en transmisión.

    Attributes
    ----------
    data : List[int]
        Datos que debe enviar la PC.
    """

    def __init__(self, name: str, signal_time: int):
        ports = {f'{name}_1' : None}
        super().__init__(name, ports)
        self.signal_time = signal_time
        self.data = []
        self.current_package = []
        self.package_index = 0
        self.time_to_send = 0
        self.max_time_to_send = 1
        self.send_time = 0
        self.sending_bit = 0
        self.is_sending = False
        self.time_connected = 0
        self.recived_bits = []

    def readjust_max_time_to_send(self):
        """
        Ajusta el tiempo máximo que será utilizado en la selección aleatoria
        de cuanto tiempo debe esperar para reintentar un envío.
        """
        self.max_time_to_send *= 2

    @property
    def cable(self):
        """Cable : Cable conectado a la PC"""
        return self.ports[self.port_name(1)]
    
    @property
    def is_connected(self):
        """bool : Estado de conección del host"""
        return self.cable is not None

    def load_package(self):
        """
        Carga el próximo paquete a enviar si hay datos.
        """
        if not self.current_package:
            if self.data:
                self.current_package = self.data[:8]
                self.data = self.data[8:]
                self.max_time_to_send = 16
                self.package_index = 0
                self.send_time = 0
                self.is_sending = True
            elif self.is_sending:
                self.sending_bit = 0
                self.is_sending = False
                self.cable.value = 0


    def update(self, time):
        super().update(time)

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

    def send(self, data: List[int]):
        """
        Agrega nuevos datos para ser enviados a la lista de datos.

        Parameters
        ----------
        data : List[int]
            Datos a ser enviados.
        """
        self.data += data

    def receive(self):
        """
        Lee del cable al que está conectado.

        Si la PC se encuentra enviando infromación entonces comprueba que no
        haya colisión.

        En caso contrario almacena la lectura del cable en varios ocaciones
        entre un ``SIGNAL_TIME`` y el siguiente. Al concluir el ``SIGNAL_TIME``
        se guarda como lectura final la moda de los datos almacenados.
        """
        if self.is_sending:
            self.check_collision()

        if self.is_sending:
            return

        elif self.time_connected % self.signal_time//3 == 0:
            self.recived_bits.append(self.cable.value)

        if self.time_connected % self.signal_time == 0 and self.recived_bits:
            temp = [(v,k) for k,v in Counter(self.recived_bits).items()]
            self.log(self.sim_time, 'Received', f'{max(temp)[1]}')
            self.recived_bits = []

    def check_collision(self):
        """
        Comprueba si existe una colisión.

        Returns
        -------
        bool
            ``True`` si hubo colisión, ``False`` en caso contrario.
        """
        if self.is_sending and self.cable.value != self.sending_bit:
            self.time_to_send = randint(1, self.max_time_to_send)
            self.readjust_max_time_to_send()
            self.log(self.sim_time,
                     'Collision',
                     f'Waitting {self.time_to_send}ms to send')
            self.package_index = 0
            self.send_time = 0
            self.is_sending = False
            return True
        return False

    def connect(self, cable: Cable, port_name: str):
        if self.cable is not None:
            raise ValueError(f'Port {port_name} is currently in use.')

        self.ports[self.port_name(1)] = cable
        self.log(self.sim_time, 'Connected')

    def disconnect(self, port_name: str):
        self.data = self.current_package + self.data
        self.current_package = []
        self.package_index = 0
        self.is_sending = False
        self.send_time = 0
        self.sending_bit = 0
        self.max_time_to_send = 16
        self.time_connected = 0
        self.recived_bits = []
        super().disconnect(port_name)
        self.log(self.sim_time, 'Disconnected')
