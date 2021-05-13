from typing import List, Tuple
from math import log, ceil
import operator as op
from functools import reduce
from nesim.devices.utils import data_size, extend_to_byte_divisor, from_bit_data_to_number

##############################################################################
#                                Check error                                 #
##############################################################################

def _simple_hash(frame: List[int]) -> Tuple[List[int], bool]:
    correction_size = from_bit_data_to_number(frame[40:48])
    data = frame[48:len(frame) - 8*correction_size]
    correction_data = frame[-8*correction_size:]
    return frame, sum(data) != from_bit_data_to_number(correction_data)

def _hamming(frame: List[int]) -> Tuple[List[int], bool]:
    correction_size = from_bit_data_to_number(frame[40:48])
    data = frame[48:len(frame) - 8*correction_size]
    correct_parity = frame[-8*correction_size:]
    _, actual_parity = _get_hamming(data)
    return frame, not all(b1 == b2 for b1, b2 in zip(correct_parity, actual_parity))

def check_frame_correction(frame: List[int],
                           error_det_algorithm: str) \
                           -> Tuple[List[int], bool]:
    if error_det_algorithm == 'simple_hash':
        return _simple_hash(frame)
    if error_det_algorithm == 'hamming':
        return _hamming(frame)
    else:
        raise ValueError('Invalid error detection algorithm')

##############################################################################
#                      Apply error correction algorithm                      #
##############################################################################

def _get_simple_hash(data: List[List[int]]) -> Tuple[List[int], List[int]]:
    data_sum = sum(data)
    bit_data_sum = f'{data_sum:b}'
    if len(bit_data_sum) % 8 != 0:
        rest = 8 - len(bit_data_sum) % 8
        bit_data_sum = '0'*rest + bit_data_sum
    error_correction = [int(b) for b in bit_data_sum]
    error_correction_size = [int(b) for b in f'{len(bit_data_sum) // 8:08b}']
    return error_correction_size, error_correction


def _get_hamming(data: List[List[int]]) -> Tuple[List[int], List[int]]:
    needed_bits = ceil(log(len(data), 2))

    # Adding the parity check bits
    data.insert(0, 0)
    for i in range(needed_bits):
        data.insert(2**i, 0)

    # Filling the data
    rest = ceil(log(len(data), 2))
    new_bits = 2**rest - len(data)
    data += [0]*new_bits

    # Filling the parity check bits
    parity = []
    for i in range(needed_bits):
        pos = 2**i
        data[pos] = reduce(op.xor,[
            bit for j, bit in enumerate(data) if bit and f'{j:0255b}'[-(i+1)] == '1'
        ])
        parity.append(data[pos])
    parity.insert(0, reduce(op.xor,parity))

    # Removing the parity check bits
    for i in range(needed_bits - 1, -1, -1):
        del data[2**i]
    del data[0]

    for i in range(new_bits):
        del data[-1]

    return data_size(parity), extend_to_byte_divisor(parity)

def get_error_detection_data(data: List[int],
                             error_det_algorithm: str) \
                             -> Tuple[List[int], List[int]]:
    if error_det_algorithm == 'simple_hash':
        return _get_simple_hash(data)
    if error_det_algorithm == 'hamming':
        return _get_hamming(data)
    else:
        raise ValueError('Invalid error detection algorithm')


if __name__ == '__main__':
    # Testing
    data = [1,1,1,1,0,0,1,0,0,1,0]
    print(_get_hamming(data))
    print(_get_simple_hash(data))
    print(data)
