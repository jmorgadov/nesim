from typing import List


def from_bit_data_to_number(data: List[int]):
    return int(''.join([str(bit for bit in data)]), 2)