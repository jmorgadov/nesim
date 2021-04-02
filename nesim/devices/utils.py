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
