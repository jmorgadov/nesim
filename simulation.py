from typing import Dict
from devices import Device, PC, Cable

SIGNAL_TIME = 10

class NetSimulation():

    def __init__(self, output_path='.'):
        self.instructions = []
        self.signal_time = SIGNAL_TIME
        self.output_path = output_path
        self.inst_index = 0
        self.time = 0
        self.pending_devices = []
        self.port_to_device: Dict[str, Device] = {}
        self.devices: Dict[str, Device] = {}
        self.hosts: Dict[str, PC] = {}
        self.end_delay = self.signal_time
    
    def is_running(self):
        device_sending = any([(d.is_sending or d.time_to_send) \
             for d in self.hosts.values()])
        running = self.instructions or device_sending
        if not running:
            self.end_delay -= 1
        return self.end_delay > 0

    def add_device(self, device: Device):
        if device.name in self.devices.keys():
            raise ValueError(f'The device name {device.name} is already taken.')

        self.devices[device.name] = device

        if isinstance(device, PC):
            self.hosts[device.name] = device

        for port in device.ports.keys():
            self.port_to_device[port] = device

    def connect(self, port1, port2):
        cab = Cable()
        self.port_to_device[port1].connect(cab, port1)
        self.port_to_device[port2].connect(cab, port2)

    def send(self, host, data):
        self.hosts[host].send(data)

    def disconnect(self, port):
        dev = self.port_to_device[port]
        for port in dev.ports.keys():
            self.port_to_device.pop(port)
        self.devices.pop(dev.name)
        if dev.name in self.hosts.keys():
            self.hosts.pop(dev.name)    

    def start(self, instructions):
        self.instructions = instructions
        self.time = 0
        while self.is_running():
            self.update()
        for d in self.devices.values():
            d.save_log()

    def update(self):
        t = self.time

        current_insts = []
        while self.instructions and t == self.instructions[0].time:
            current_insts.append(self.instructions.pop(0))

        for instr in current_insts:
            instr.execute(self)

        for device in self.devices.values():
            if device not in self.hosts.values():
                device.reset()

        for host in self.hosts.values():
            host.update(t)

        for _ in range(len(self.devices)):
            for device in self.devices.values():
                if device not in self.hosts.values():
                    device.update(t)

        for host in self.hosts.values():
            host.receive()
        
        self.time += 1
