from typing import List

def from_bit_data_to_number(data: List[int]):
    """Convierte los datos de una lista de bits a un número en base decimal.

    Parameters
    ----------
    data : List[int]
        Datos a convertir.

    Returns
    -------
    int
        Número resultante.
    """

    return int(''.join([str(bit) for bit in data]), 2)

def from_str_to_bin(s: str):
    return ''.join([f'{ord(c):08b}' for c in s])

def from_str_to_bit_data(s: str):
    return [int(b) for b in from_str_to_bin(s)]

def data_size(data):
    size_str = f'{len(data)//8:b}'
    size = [0]*8

    for i in range(1,len(size_str) + 1):
        size[-i] = int(size_str[-i])
    return size
