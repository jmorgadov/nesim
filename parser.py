import instructions as inst

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
                #Instruccion para el hub
                pass
            else:
                #Instruccion para el host
        elif inst_name == 'connect':
            first_port = temp_line[2]
            second_port = temp_line[3]
            #Instruccion para el connect
            pass
        elif inst_name == 'send':
            host_name = temp_line[2]
            data = [int(bit) for bit in temp_line[3]]
            #Instruccion para el send
            pass
        elif inst_name == 'disconnect':
            port_name = temp_line[2]
            #Instruccion para el disconnect
            pass

    return inst_list