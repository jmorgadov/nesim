import abc
from pathlib import Path
from typing import Dict
import logging
from nesim.devices.send_receiver import SendReceiver
from nesim.devices.cable import DuplexCableHead


class Device(metaclass=abc.ABCMeta):
    """
    Representa un dispositivo.

    Parameters
    ----------
    name : str
        Nombre del dispositivo.
    ports : Dict[str, SendReceiver]
        Puertos del dispositivo.

        Cada puerto está asociado a un ``SendReceiver``. Si para un puerto
        dado el cable asociado al ``SendReceiver`` es ``None`` significa
        que este puerto no tiene ningún cable conectado.

    Attributes
    ----------
    name : str
        Nombre del dispositivo.
    ports : Dict[str, SendReceiver]
        Puertos del dispositivo.

        Cada puerto está asociado a un ``SendReceiver``. Si para un puerto
        dado el cable asociado al ``SendReceiver`` es ``None`` significa
        que este puerto no tiene ningún cable conectado.
    logs : List[str]
        Logs del dispositivo.
    sim_time : int
        Timepo de ejecución de la simulación.

        Este valor se actualiza en cada llamado a la función ``update``.
    """

    def __init__(self, name: str, ports: Dict[str, SendReceiver]):
        self.name = name
        self.ports = ports
        self.logs = []
        self.sim_time = 0

    @abc.abstractproperty
    def is_active(self):
        """bool : Estado del dispositivo."""

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
    def connect(self, cable_head: DuplexCableHead, port_name: str):
        """
        Conecta un cable dado a un puerto determinado.

        Parameters
        ----------
        cable_head : DuplexCableHead
            Uno de los extremos del cable a conectar.
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
