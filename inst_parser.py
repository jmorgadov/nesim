from instructions import (
    CreateHostIns,
    CreateHubIns,
    SendIns,
    ConnectIns,
    DisconnectIns
)
from typing import List

def parse_single_inst(inst_text: str):

    temp_line = inst_text.split()
    inst_time = int(temp_line[0])
    inst_name = temp_line[1]

    if inst_name == 'create':
        device_type = temp_line[2]
        device_name = temp_line[3]
        if device_type == 'hub':
            cant_ports = int(temp_line[4])
            return CreateHubIns(inst_time, device_name, cant_ports)
        else:
            return CreateHostIns(inst_time, device_name)

    elif inst_name == 'connect':
        first_port = temp_line[2]
        second_port = temp_line[3]
        return ConnectIns(inst_time, first_port, second_port)

    elif inst_name == 'send':
        host_name = temp_line[2]
        data = [int(bit) for bit in temp_line[3]]
        return SendIns(inst_time, host_name, data)

    else:
        port_name = temp_line[2]
        return DisconnectIns(inst_time, port_name)

def parse_instructions(instr_lines: List[str]):
    return [parse_single_inst(line) for line in instr_lines]
