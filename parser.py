from instructions import *

def parse_instructions(text:str):
    inst_list = []
    inst_lines = text.split('\n')
    for i in inst_lines:
        temp_line = i.split()
        inst_time = int(temp_line[0])
        inst_name = temp_line[1]
        if inst_name == 'create':
            device_type = temp_line[2]
            device_name = temp_line[3]
            if device_type == 'hub':
                cant_ports = int(temp_line[4])
                inst_list.append(CreateHubIns(inst_time, device_name, cant_ports))
            else:
                inst_list.append(CreateHostIns(inst_time, device_name))
        elif inst_name == 'connect':
            first_port = temp_line[2]
            second_port = temp_line[3]
            inst_list.append(ConnectIns(inst_time, first_port, second_port))
        elif inst_name == 'send':
            host_name = temp_line[2]
            data = [int(bit) for bit in temp_line[3]]
            inst_list.append(SendIns(inst_time, host_name, data))
        else:
            port_name = temp_line[2]
            inst_list.append(DisconnectIns(inst_time, port_name))

    return inst_list