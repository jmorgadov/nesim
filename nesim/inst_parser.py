from typing import List
from pathlib import Path
from nesim.instructions import (
    CreateHostIns,
    CreateHubIns,
    CreateSwitchIns,
    MacIns,
    SendIns,
    SendFrameIns,
    ConnectIns,
    DisconnectIns
)

def _to_binary(hex_num: str, fmt: str = '016b'):
    """Convierte una representación hexagesimal a binaria.

    Parameters
    ----------
    hex_num : str
        Número hexagesimal.
    fmt : str, optional
        Formato usado para convertir, por defecto ``016b``.

    Returns
    -------
    str
        Número convertido.
    """

    return format(int(hex_num, base=16), fmt)

def _parse_single_inst(inst_text: str):

    temp_line = inst_text.split()
    inst_time = int(temp_line[0])
    inst_name = temp_line[1]

    if inst_name == 'create':
        device_type = temp_line[2]
        device_name = temp_line[3]
        if device_type == 'hub':
            cant_ports = int(temp_line[4])
            return CreateHubIns(inst_time, device_name, cant_ports)
        elif device_type == 'switch':
            cant_ports = int(temp_line[4])
            return CreateSwitchIns(inst_time, device_name, cant_ports)
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

    elif inst_name == 'mac':
        host_name = temp_line[2]
        address = [int(i) for i in _to_binary(temp_line[3])]
        return MacIns(inst_time, host_name, address)

    elif inst_name == 'send_frame':
        host_name = temp_line[2]
        mac = [int(i) for i in _to_binary(temp_line[3])]
        data = [int(i) for i in _to_binary(temp_line[4])]
        return SendFrameIns(inst_time, host_name, mac, data)

    else:
        port_name = temp_line[2]
        return DisconnectIns(inst_time, port_name)

def parse_instructions(instr_lines: List[str]):
    """
    Parsea una lista de instrucciones.

    Parameters
    ----------
    instr_lines : List[str]
        Lista de instrucciones en modo de texto.

    Returns
    -------
    List[Instruction]
        Lista de instrucciones.
    """
    return [_parse_single_inst(line) for line in instr_lines]

def load_instructions(inst_path: str = './script.txt'):
    """
    Carga una serie de instrucciones de un archivo.

    Parameters
    ----------
    inst_path : str
        Ruta del archivo que contiene las instrucciones.

    Returns
    -------
    List[Instruction]
        Lista de instrucciones cargadas del archivo.

    Raises
    ------
    ValueError
        Si la ruta del archivo es inválida.
    """

    path = Path(inst_path)
    if path.exists():
        raw_inst = []
        with open(str(path), 'r') as file:
            raw_inst = file.readlines()
        return parse_instructions(raw_inst)
    else:
        raise ValueError(f"Invalid path '{inst_path}'")
