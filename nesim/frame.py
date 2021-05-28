from typing import List
from nesim.devices.utils import from_bit_data_to_number


class Frame():

    def __init__(self, bit_data: List[int]) -> None:
        self.is_valid = False

        if len(bit_data) < 48:
            return

        self.to_mac = from_bit_data_to_number(bit_data[:16])
        self.from_mac = from_bit_data_to_number(bit_data[16:32])
        size = from_bit_data_to_number(bit_data[32:40]) * 8
        size += from_bit_data_to_number(bit_data[40:48]) * 8

        if len(bit_data) - 48 < size:
            return

        self.bit_data = bit_data
        self.is_valid = True
