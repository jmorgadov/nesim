from random import randint, random
from typing import Dict, List, Tuple
from pathlib import Path
from nesim.devices.send_receiver import SendReceiver
from nesim.devices.device import Device
from nesim.devices.cable import DuplexCableHead
from nesim.devices.utils import from_bit_data_to_number, from_str_to_bin, data_size, from_str_to_bit_data
from nesim.devices.error_detection import check_frame_correction, get_error_detection_data
from nesim.ip import IP
import nesim.utils as utils

class Host(Device):
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
        self.signal_time = signal_time
        self.mac = None
        self.ip: IP = None
        self.ip_mask: IP = None
        self.send_receiver = self.create_send_receiver()
        ports = {f'{name}_1' : self.send_receiver}

        self.ip_table: Dict[str: List[int]] = {}
        self.waiting_for_arpq: Dict[str: List[int]] = {}

        # Data receiving stuff
        self.received_data = []
        self.buffer = []
        self.is_receiving_data = False
        self.frame_start_index = 0
        self.data_size = None
        self.data_error_size = None
        self.data_from = None

        super().__init__(name, ports)

    @property
    def str_mac(self):
        """str : Dirección mac del host."""
        if self.mac is not None:
            return ''.join(map(str, self.mac))

    @property
    def cable_head(self):
        """DuplexCableHead : Extremo del cable conectado a la PC"""
        return self.ports[self.port_name(1)]

    @property
    def is_connected(self):
        """bool : Estado de conección del host"""
        return self.send_receiver is not None and \
               self.send_receiver.cable_head is not None

    @property
    def is_active(self):
        return self.send_receiver.is_active

    def check_subnet(self, subnet_ip: IP) -> bool:
        """Checks if the host belogns to a given subnet

        Parameters
        ----------
        subnet_ip : IP
            Subnet IP

        Returns
        -------
        bool
            True if the host belongs to the subnet
        """

        return self.ip.check_subnet(subnet_ip, self.ip_mask)

    def save_log(self, path: str = ''):
        super().save_log(path=path)

        output_path = Path(path) / Path(f'{self.name}_data.txt')
        with open(output_path, 'w+') as data_file:
            data = [' '.join(map(str, d)) + '\n' for d in self.received_data]
            data_file.writelines(data)

    def update(self, time):
        super().update(time)
        self.send_receiver.update()

    def send(self, data: List[int], package_size = None):
        """
        Agrega nuevos datos para ser enviados a la lista de datos.

        Parameters
        ----------
        data : List[List[int]]
            Datos a ser enviados.
        """

        if package_size is None:
            package_size = len(data)

        packages = []
        while data:
            packages.append(data[:package_size])
            data = data[package_size:]

        self.send_receiver.send(packages)

    def build_frame(self, mac: List[int], data: List[int]):

        data += [0]*(len(data) % 8)

        e_size, e_data = get_error_detection_data(
            data, utils.CONFIG['error_detection']
        )

        rand = random()
        if rand < 1e-10:
            ind = randint(0, len(data) - 1)
            data[ind] = (data[ind] + 1) % 2

        size = data_size(data)
        final_data = mac + \
                     self.mac + \
                     size + \
                     e_size + \
                     data + \
                     e_data

        return final_data

    def send_frame(self, mac: List[int], data: List[int]):
        """
        Ordena a un host a enviar un frame determinado a una dirección mac
        determinada.

        Parameters
        ----------
        host_name : str
            Nombre del host que envía la información.
        mac : List[int]
            Mac destino.
        data : List[int]
            Frame a enviar.
        """

        self.send(self.build_frame(mac, data))

    def find_mac(self, ip: IP):
        arpq = from_str_to_bit_data('ARPQ')
        ip_data = ip.bit_data
        self.send_frame([1]*16, arpq + ip_data)


    def send_ip_package(self, ip_dest: IP, data: List[int]):
        package = ip_dest.bit_data + \
                  self.ip.bit_data + \
                  [0] * 8 + \
                  [0] * 8 + \
                  data_size(data) + \
                  data
        ip_dest_str = str(ip_dest)
        if ip_dest_str not in self.ip_table:
            if ip_dest_str not in self.waiting_for_arpq:
                self.waiting_for_arpq[ip_dest_str] = []
            self.waiting_for_arpq[ip_dest_str].append(package)
            self.find_mac(ip_dest)
        else:
            self.send_frame(self.ip_table[ip_dest_str], package)

    def receive(self):
        """
        Lee del cable al que está conectado.

        Si la PC se encuentra enviando infromación entonces comprueba que no
        haya colisión.

        En caso contrario almacena la lectura del cable en varios ocaciones
        entre un ``SIGNAL_TIME`` y el siguiente. Al concluir el ``SIGNAL_TIME``
        se guarda como lectura final la moda de los datos almacenados.
        """
        self.send_receiver.receive()

    def check_errors(self, frame) -> Tuple[List[int], bool]:
        utils.check_config()
        error_det_algorith = utils.CONFIG['error_detection']
        return check_frame_correction(frame, error_det_algorith)

    def receive_frame(self, frame):
        mac_dest = frame[:16]
        mac_dest_str = ''.join([str(b) for b in mac_dest])
        mac_origin = frame[16:32]
        data_s = from_bit_data_to_number(frame[32:40])
        data = frame[48: 48 + 8*data_s]

        # ARPQ protocol
        if data_s == 8:
            arpq = from_str_to_bin('ARPQ')
            ip = ''.join([str(b) for b in data[32:]])
            if mac_dest_str == '1'*16:
                arpq_data = ''.join([str(b) for b in data[:32]])
                if arpq_data.endswith(arpq) and \
                    ip == self.ip.str_binary:
                    self.send_frame(mac_origin, data)
            else:
                new_ip = IP.from_bin(ip)
                self.ip_table[str(new_ip)] = mac_origin
                if str(new_ip) in self.waiting_for_arpq:
                    for data in self.waiting_for_arpq[str(new_ip)]:
                        self.send_frame(mac_origin, data)


    def received_bit(self, bit: int):
        """
        Se ejecuta cada vez que el host recibe un bit. Procesa la información
        en el buffer para indentificar frames cuyo destino sea el host en
        cuestión.

        Parameters
        ----------
        bit : int
            Bit recibido.
        """

        self.log(self.sim_time, 'Received', f'{bit}')
        self.buffer.append(bit)

        if bit is None:
            self.is_receiving_data = False
            self.buffer = []
            self.data_from = None
            self.frame_start_index = 0
            self.data_size = 0
            return

        if self.is_receiving_data:
            received_size = len(self.buffer) - self.frame_start_index
            fsi = self.frame_start_index
            if received_size == 48:
                _from = from_bit_data_to_number(
                    self.buffer[fsi + 16:fsi + 32]
                )
                self.data_from = str(hex(_from))[2:].upper()
                self.data_size = from_bit_data_to_number(
                    self.buffer[fsi + 32:fsi + 40]
                )
                self.data_error_size = from_bit_data_to_number(
                    self.buffer[fsi + 40:fsi + 48]
                )
            elif received_size > 48 and \
                received_size == fsi + 48 + 8*self.data_size + 8*self.data_error_size:
                frame, error = self.check_errors(self.buffer[fsi:])
                data = from_bit_data_to_number(frame[48:48+8*self.data_size])
                hex_data = str(hex(data))[2:].upper()
                if len(hex_data) % 4 != 0:
                    rest = 4 - len(hex_data) % 4
                    hex_data = '0'*rest + hex_data
                r_data = [self.sim_time, self.data_from, hex_data]
                if error:
                    r_data.append('ERROR')
                else:
                    self.receive_frame(frame)
                self.received_data.append(r_data)
                self.buffer = []
                self.is_receiving_data = False
                self.buffer = []
                self.data_from = None
                self.frame_start_index = 0
                self.data_size = 0
                return

        last = self.buffer[-16:]
        last_str = ''.join(map(str, last))
        if not self.is_receiving_data and last_str == self.str_mac or last_str == '1'*16:
            self.is_receiving_data = True
            self.frame_start_index = len(self.buffer) - 16


    def create_send_receiver(self):
        """Crea un ``SendReceiver``.

        Returns
        -------
        SendReceiver
            ``SendReceiver`` creado.
        """

        send_receiver = SendReceiver(self.signal_time)

        send_receiver.on_send.append(
            lambda bit: self.log(self.sim_time, 'Sent', f'{bit}')
        )

        send_receiver.on_receive.append(
            lambda bit: self.received_bit(bit)
        )

        send_receiver.on_collision.append(
            lambda : self.log(self.sim_time,
                     'Collision',
                     f'Waitting {send_receiver.time_to_send}ms to send')
        )
        return send_receiver

    def connect(self, cable_head: DuplexCableHead, port_name: str):
        if self.send_receiver.cable_head is not None:
            raise ValueError(f'Port {port_name} is currently in use.')

        self.send_receiver.cable_head = cable_head

        self.log(self.sim_time, 'Connected')

    def disconnect(self, port_name: str):
        self.send_receiver.disconnect()
        self.log(self.sim_time, 'Disconnected')
