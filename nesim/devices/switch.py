from nesim.frame import Frame
from nesim.devices.multiple_port_device import MultiplePortDevice


class Switch(MultiplePortDevice):
    """Representa un switch en la simulación."""

    def on_frame_received(self, frame: Frame, port: str) -> None:
        self.mac_table[frame.from_mac] = self.port_name(port + 1)

        if frame.to_mac in self.mac_table:
            self.ports[self.mac_table[frame.to_mac]].send([frame.bit_data])
        else:
            self.broadcast(self.port_name(port + 1), [frame.bit_data])
        self.ports_buffer[port] = []
