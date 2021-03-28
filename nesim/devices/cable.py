
class Cable():
    """
    Representa un cable físico.

    Attributes
    ----------
    value : int
        Valor del bit que se transmite.
    """

    def __init__(self):
        self.value = 0


class DuplexCableHead():

    def __init__(self, receive_cable, send_cable):
        self.receive_cable: Cable = receive_cable
        self.send_cable: Cable = send_cable

    def send(self, bit):
        self.send_cable.value = bit

    def receive(self):
        return self.receive_cable.value
   
    @property
    def send_value(self):
        return self.send_cable.value

    @property
    def receive_value(self):
        return self.receive_cable.value

class Duplex():

    def __init__(self):
        c1, c2 = Cable(), Cable()
        self.head_1 = DuplexCableHead(c1, c2)
        self.head_2 = DuplexCableHead(c2, c1)

    @property
    def h1(self):
        return self.head_1

    @property
    def h2(self):
        return self.head_2