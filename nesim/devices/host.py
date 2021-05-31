from nesim.devices.send_receiver import SendReceiver
from typing import List, Tuple
from pathlib import Path
from nesim.devices.router import Router
from nesim.frame import Frame
from nesim.devices.utils import (
    from_bit_data_to_hex,
    from_bit_data_to_number, from_number_to_bit_data
)
from nesim.devices.error_detection import check_frame_correction
from nesim.ip import IP, IPPacket
import nesim.utils as utils


class Host(Router):
    """Representa un host."""

    def __init__(self, name: str, signal_time: int):
        self.received_data = []
        self.received_payload = []
        super().__init__(name, 1, signal_time)

    def send_ping_to(self, to_ip: IP) -> None:
        """
        Envia un paquete IP a una dirección haciendo ``ping``.

        Parameters
        ----------
        to_ip : IP
            IP destino.
        """

        self.send_ip_packet(IPPacket.ping(to_ip, self.ip))

    def send_ip_packet(self, packet: IPPacket, port: int = 1,
                       ip_dest: IP = None) -> None:
        self.enroute(packet)

    def save_log(self, path: str = ''):
        output_path = Path(path) / Path(f'{self.name}_data.txt')
        with open(output_path, 'w+') as data_file:
            data = [' '.join(map(str, d)) + '\n' for d in self.received_data]
            data_file.writelines(data)

        output_path = Path(path) / Path(f'{self.name}_payload.txt')
        with open(output_path, 'w+') as data_file:
            data = [' '.join(map(str, d)) + '\n' for d in self.received_payload]
            data_file.writelines(data)

    @property
    def send_receiver(self) -> SendReceiver:
        """SendReceiver : Send-Recever del host"""
        return self.ports[self.port_name(0)]

    @property
    def ip(self) -> IP:
        """IP : IP del host"""
        return self.ips[1]

    def check_errors(self, frame: List[int]) -> Tuple[List[int], bool]:
        """
        Checkea errores en un frame.

        Parameters
        ----------
        frame : List[int]
            Frame a checkear.

        Returns
        -------
        List[int]
            Frame comprobado
        bool
            True si hubo algún error
        """        
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

    def on_ip_packet_received(self, packet: IPPacket, port: int = 1, frame: Frame = None) -> None:
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
