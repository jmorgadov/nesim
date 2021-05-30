from nesim.devices.ip_packet_sender import IPPacketSender
from typing import Dict, List, Tuple
from pathlib import Path
from nesim.devices.router import RouteTable, Router
from nesim.frame import Frame
from nesim.devices.send_receiver import SendReceiver
from nesim.devices.device import Device
from nesim.devices.cable import DuplexCableHead
from nesim.devices.utils import (
    from_bit_data_to_hex,
    from_bit_data_to_number, from_number_to_bit_data,
    from_str_to_bin, data_size,
    from_str_to_bit_data
)
from nesim.devices.error_detection import check_frame_correction
from nesim.ip import IP, IPPacket
import nesim.utils as utils


class Host(Router):

    def __init__(self, name: str, signal_time: int):
        self.received_data = []
        self.received_payload = []
        super().__init__(name, 1, signal_time)
    
    def send_ping_to(self, to_ip: IP) -> None:
        self.send_ip_packet(IPPacket.ping(to_ip, self.ip))

    def send_ip_packet(self, packet: IPPacket, port: int = 1,
                       ip_dest: IP = None) -> None:
        self.enroute(packet)

    def save_log(self, path: str = ''):
        # super().save_log(path=path)

        output_path = Path(path) / Path(f'{self.name}_data.txt')
        with open(output_path, 'w+') as data_file:
            data = [' '.join(map(str, d)) + '\n' for d in self.received_data]
            data_file.writelines(data)

        output_path = Path(path) / Path(f'{self.name}_payload.txt')
        with open(output_path, 'w+') as data_file:
            data = [' '.join(map(str, d)) + '\n' for d in self.received_payload]
            data_file.writelines(data)

    @property
    def send_receiver(self):
        return self.ports[self.port_name(0)]
    
    @property
    def ip(self):
        return self.ips[1]

    def check_errors(self, frame) -> Tuple[List[int], bool]:
        utils.check_config()
        error_det_algorith = utils.CONFIG['error_detection']
        return check_frame_correction(frame, error_det_algorith)

    def on_frame_received(self, frame: Frame, port: str) -> None:
        frame, error = self.check_errors(frame.bit_data)
        frame = Frame(frame)
        data_from = from_bit_data_to_hex(from_number_to_bit_data(frame.from_mac))
        hex_data = from_bit_data_to_hex(frame.data)
        r_data = [self.sim_time, data_from, hex_data]
        if error:
            r_data.append('ERROR')
        else:
            super().on_frame_received(frame, 1)
        self.received_data.append(r_data)

    def on_ip_packet_received(self, packet: IPPacket, port: int = 1) -> None:
        if packet.to_ip != self.ip:
            return

        r_data = [self.sim_time, str(packet.from_ip)]

        # Is ICMP protocol
        if packet.protocol_number == 1:
            payload_number = from_bit_data_to_number(packet.payload)
            if payload_number == 8:
                self.send_ip_packet(IPPacket.pong(packet.from_ip, self.ip))
            r_data.append(packet.icmp_payload_msg)
        else:
            hex_data = from_bit_data_to_hex(packet.payload)
            r_data.append(hex_data)
        self.received_payload.append(r_data)


# class Host(IPPacketSender, RouteTable):
#     """
#     Representa una PC (Host).

#     Parameters
#     ----------
#     name : str
#         Nombre de la PC.
#     signal_time : int
#         Tiempo mínimo que debe estar un bit en transmisión.

#     Attributes
#     ----------
#     data : List[int]
#         Datos que debe enviar la PC.
#     """

#     def __init__(self, name: str, signal_time: int):
#         self.signal_time = signal_time
#         self.send_receiver = self.create_send_receiver()
#         ports = {f'{name}_1' : self.send_receiver}

#         self.received_payload = []

#         # Data receiving stuff
#         self.received_data = []
#         self.buffer = []
#         self.is_receiving_data = False
#         self.frame_start_index = 0
#         self.data_size = None
#         self.data_error_size = None
#         self.data_from = None

#         super().__init__(name, ports)

#     @property
#     def str_mac(self):
#         """str : Dirección mac del host."""
#         if self.mac is not None:
#             return ''.join(map(str, self.mac))

#     @property
#     def cable_head(self):
#         """DuplexCableHead : Extremo del cable conectado a la PC"""
#         return self.ports[self.port_name(1)]

#     @property
#     def is_connected(self):
#         """bool : Estado de conección del host"""
#         return self.send_receiver is not None and \
#                self.send_receiver.cable_head is not None

#     @property
#     def is_active(self):
#         return self.send_receiver.is_active

#     def check_subnet(self, subnet_ip: IP) -> bool:
#         """Checks if the host belogns to a given subnet

#         Parameters
#         ----------
#         subnet_ip : IP
#             Subnet IP

#         Returns
#         -------
#         bool
#             True if the host belongs to the subnet
#         """

#         return self.ip.check_subnet(subnet_ip, self.ip_mask)

#     def save_log(self, path: str = ''):
#         super().save_log(path=path)

#         output_path = Path(path) / Path(f'{self.name}_data.txt')
#         with open(output_path, 'w+') as data_file:
#             data = [' '.join(map(str, d)) + '\n' for d in self.received_data]
#             data_file.writelines(data)

#         output_path = Path(path) / Path(f'{self.name}_payload.txt')
#         with open(output_path, 'w+') as data_file:
#             data = [' '.join(map(str, d)) + '\n' for d in self.received_payload]
#             data_file.writelines(data)

#     def update(self, time):
#         super().update(time)
#         self.send_receiver.update()

#     def send_ping_to(self, to_ip: IP) -> None:
#         self.send_ip_packet(IPPacket.ping(to_ip, self.ip))

#     def receive(self):
#         """
#         Lee del cable al que está conectado.

#         Si la PC se encuentra enviando infromación entonces comprueba que no
#         haya colisión.

#         En caso contrario almacena la lectura del cable en varios ocaciones
#         entre un ``SIGNAL_TIME`` y el siguiente. Al concluir el ``SIGNAL_TIME``
#         se guarda como lectura final la moda de los datos almacenados.
#         """
#         self.send_receiver.receive()

#     def check_errors(self, frame) -> Tuple[List[int], bool]:
#         utils.check_config()
#         error_det_algorith = utils.CONFIG['error_detection']
#         return check_frame_correction(frame, error_det_algorith)

#     def receive_frame(self, frame):
#         mac_dest = frame[:16]
#         mac_dest_str = ''.join([str(b) for b in mac_dest])
#         mac_origin = frame[16:32]
#         data_s = from_bit_data_to_number(frame[32:40])
#         data = frame[48: 48 + 8*data_s]

#         # ARPQ protocol
#         if data_s == 8:
#             arpq = from_str_to_bin('ARPQ')
#             ip = ''.join([str(b) for b in data[32:]])
#             if mac_dest_str == '1'*16:
#                 arpq_data = ''.join([str(b) for b in data[:32]])
#                 if arpq_data.endswith(arpq) and \
#                     ip == self.ip.str_binary:
#                     self.send_frame(mac_origin, data)
#             else:
#                 new_ip = IP.from_bin(ip)
#                 self.ip_table[str(new_ip)] = mac_origin
#                 if str(new_ip) in self.waiting_for_arpq:
#                     for data in self.waiting_for_arpq[str(new_ip)]:
#                         self.send_frame(mac_origin, data)
#                     self.waiting_for_arpq[str(new_ip)] = []

#         # Check IP-Packet
#         valid_ip_packet, ip_packet = IPPacket.parse(data)
#         if valid_ip_packet and ip_packet.to_ip == self.ip:
#             r_data = [self.sim_time, str(ip_packet.from_ip)]
#             # Is ICMP protocol
#             if ip_packet.protocol_number == 1:
#                 payload_number = from_bit_data_to_number(ip_packet.payload)
#                 if payload_number == 8:
#                     self.send_ip_packet(IPPacket.pong(ip_packet.from_ip, self.ip))
#                 r_data.append(ip_packet.icmp_payload_msg)
#             else:
#                 hex_data = from_bit_data_to_hex(ip_packet.payload)
#                 r_data.append(hex_data)
#             self.received_payload.append(r_data)

#     def received_bit(self, bit: int):
#         """
#         Se ejecuta cada vez que el host recibe un bit. Procesa la información
#         en el buffer para indentificar frames cuyo destino sea el host en
#         cuestión.

#         Parameters
#         ----------
#         bit : int
#             Bit recibido.
#         """

#         self.log(self.sim_time, 'Received', f'{bit}')
#         self.buffer.append(bit)

#         if bit is None:
#             self.is_receiving_data = False
#             self.buffer = []
#             self.data_from = None
#             self.frame_start_index = 0
#             self.data_size = 0
#             return

#         if self.is_receiving_data:
#             received_size = len(self.buffer) - self.frame_start_index
#             fsi = self.frame_start_index
#             if received_size == 48:
#                 _from = from_bit_data_to_number(
#                     self.buffer[fsi + 16:fsi + 32]
#                 )
#                 self.data_from = str(hex(_from))[2:].upper()
#                 self.data_size = from_bit_data_to_number(
#                     self.buffer[fsi + 32:fsi + 40]
#                 )
#                 self.data_error_size = from_bit_data_to_number(
#                     self.buffer[fsi + 40:fsi + 48]
#                 )
#             elif received_size > 48 and \
#                 received_size == fsi + 48 + 8*self.data_size + 8*self.data_error_size:
#                 frame, error = self.check_errors(self.buffer[fsi:])
#                 data = from_bit_data_to_number(frame[48:48+8*self.data_size])
#                 hex_data = str(hex(data))[2:].upper()
#                 if len(hex_data) % 4 != 0:
#                     rest = 4 - len(hex_data) % 4
#                     hex_data = '0'*rest + hex_data
#                 r_data = [self.sim_time, self.data_from, hex_data]
#                 if error:
#                     r_data.append('ERROR')
#                 else:
#                     self.receive_frame(frame)
#                 self.received_data.append(r_data)
#                 self.buffer = []
#                 self.is_receiving_data = False
#                 self.buffer = []
#                 self.data_from = None
#                 self.frame_start_index = 0
#                 self.data_size = 0
#                 return

#         last = self.buffer[-16:]
#         last_str = ''.join(map(str, last))
#         if not self.is_receiving_data and last_str == self.str_mac or last_str == '1'*16:
#             self.is_receiving_data = True
#             self.frame_start_index = len(self.buffer) - 16


#     def create_send_receiver(self):
#         """Crea un ``SendReceiver``.

#         Returns
#         -------
#         SendReceiver
#             ``SendReceiver`` creado.
#         """

#         send_receiver = SendReceiver(self.signal_time)

#         send_receiver.on_send.append(
#             lambda bit: self.log(self.sim_time, 'Sent', f'{bit}')
#         )

#         send_receiver.on_receive.append(
#             lambda bit: self.received_bit(bit)
#         )

#         send_receiver.on_collision.append(
#             lambda : self.log(self.sim_time,
#                      'Collision',
#                      f'Waitting {send_receiver.time_to_send}ms to send')
#         )
#         return send_receiver

#     def connect(self, cable_head: DuplexCableHead, port_name: str):
#         if self.send_receiver.cable_head is not None:
#             raise ValueError(f'Port {port_name} is currently in use.')

#         self.send_receiver.cable_head = cable_head

#         self.log(self.sim_time, 'Connected')

#     def disconnect(self, port_name: str):
#         self.send_receiver.disconnect()
#         self.log(self.sim_time, 'Disconnected')
