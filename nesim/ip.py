

class IP():
    """IP basic class

    Raises
    ------
    ValueError
        If the given values are not between 0 and 255
    """

    def __init__(self, *numbers):
        self.raw_value = 0
        for i in range(len(numbers)):
            num = numbers[-(i + 1)]
            if not 0 <= num <= 255:
                raise ValueError('IP numbers mut be between 0 and 255')

            self.raw_value += (num << i * 8)
        self.values = numbers

    @staticmethod
    def from_str(ip_str: str):
        values = [int(e) for e in ip_str.split('.')]
        return IP(*values)

    @staticmethod
    def from_bin(ip_bin: str):
        vals = []
        for i in range(len(ip_bin) // 8):
            vals.append(int(ip_bin[i*8:8+i*8], base=2))
        return IP(*vals)

    def check_subnet(self, subnet, mask) -> bool:
        """Check if the IP belongs to a certain subnet using a given mask.

        Parameters
        ----------
        subnet : IP
            Subnet ip
        mask : IP
            Mask ip

        Returns
        -------
        bool
            True if the IP belongs to the subnet.
        """

        return self.raw_value & mask.raw_value == subnet.raw_value

    @property
    def str_binary(self):
        """str: Binary representation of the IP"""
        return f'{self.raw_value:032b}'

    @property
    def bit_data(self):
        """str: Binary representation of the IP"""
        return [int(b) for b in self.str_binary]

    def __repr__(self):
        """str: Value representation of the IP"""
        return '.'.join([str(v) for v in self.values])

    def __str__(self) -> str:
        return self.__repr__()

    def __eq__(self, o: object) -> bool:
        return self.raw_value == o.raw_value
