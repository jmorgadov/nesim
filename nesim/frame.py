from __future__ import annotations
from typing import List
from random import randint, random
from nesim.ip import IP
from nesim import utils
from nesim.devices.error_detection import get_error_detection_data
from nesim.devices.utils import data_size, extend_to_byte_divisor, from_bit_data_to_number, from_str_to_bin


class Frame():

    def __init__(self, bit_data: List[int]) -> None:
        self.is_valid = False

        if len(bit_data) < 48:
            return

        self.to_mac = from_bit_data_to_number(bit_data[:16])
        self.from_mac = from_bit_data_to_number(bit_data[16:32])
        self.frame_data_size = from_bit_data_to_number(bit_data[32:40]) * 8
        self.error_size = from_bit_data_to_number(bit_data[40:48]) * 8
        total_size = self.frame_data_size + self.error_size

        if len(bit_data) - 48 < total_size:
            return

        top_data_pos = 48 + 8*self.frame_data_size
        self.data = bit_data[48: top_data_pos]
        self.error_data = bit_data[top_data_pos: top_data_pos + 8 * self.error_size]
        self.bit_data = bit_data
        self.is_valid = True

    @staticmethod
    def build(dest_mac: List[int], orig_mac: List[int], data: List[int]) -> Frame:
        data = extend_to_byte_divisor(data)

        e_size, e_data = get_error_detection_data(
            data, utils.CONFIG['error_detection']
        )

        rand = random()
        if rand < utils.CONFIG['error_prob']:
            ind = randint(0, len(data) - 1)
            data[ind] = (data[ind] + 1) % 2

        size = data_size(data)
        final_data = dest_mac + \
                     orig_mac + \
                     size + \
                     e_size + \
                     data + \
                     e_data

        frame = Frame(final_data)
        return frame
