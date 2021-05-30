import abc
from nesim.frame import Frame
from typing import Dict, List
from nesim.devices.utils import from_number_to_bit_data, from_str_to_bin, from_str_to_bit_data
from nesim.ip import IP, IPPacket
from nesim.devices.frame_sender import FrameSender


class IPPacketSender(FrameSender, metaclass=abc.ABCMeta):

    ip: IP = None
    ip_mask: IP = None
    ip_table: Dict[str, List[int]] = {}
    waiting_for_arpq: Dict[str, List[int]] = {}

    def find_mac(self, ip: IP, port: int = 1):
        """
        Envía un broadcast siguiendo el protocolo ARP para obtener la
        mac de un IP determinado.

        Parameters
        ----------
        ip : IP
            Ip del cual se quiere obtener la mac.
        """

        arpq = from_str_to_bit_data('ARPQ')
        ip_data = ip.bit_data
        self.send_frame([1]*16, arpq + ip_data, port)

    def send_ip_packet(self, packet: IPPacket, port: int = 1) -> None:
        """
        Envía un IP packet.

        Parameters
        ----------
        packet : IPPacket
            Paquete a enviar.
        """

        ip_dest_str = str(packet.to_ip)
        if ip_dest_str not in self.ip_table:
            if ip_dest_str not in self.waiting_for_arpq:
                self.waiting_for_arpq[ip_dest_str] = []
            self.waiting_for_arpq[ip_dest_str].append(packet.bit_data)
            self.find_mac(packet.to_ip, port)
        else:
            self.send_frame(self.ip_table[ip_dest_str], packet.bit_data, port)

    def send_by_ip(self, ip_dest: IP, data: List[int], port: int = 1) -> None:
        """
        Envía los datos dados a un IP determinado.

        Parameters
        ----------
        ip_dest : IP
            Ip destino.
        data : List[int]
            Datos a enviar.
        """

        self.send_ip_packet(IPPacket(ip_dest, self.ip, data), port)
