class Cable():
    """
    Representa un cable físico.

    Attributes
    ----------
    value : int
        Valor del bit que se transmite.
    """

    def __init__(self):
        self.value = None


class DuplexCableHead():
    """Extremo de un cablde duplex

    Parameters
    ----------
    receive_cable : Cable
        Cable por el cual se reciben los datos.
    send_cable : Cable
        Cable por el cual se envían los datos.
    """

    def __init__(self, receive_cable, send_cable):
        self.receive_cable: Cable = receive_cable
        self.send_cable: Cable = send_cable

    def send(self, bit):
        """Escribe un bit en el cablde de escritura.

        Parameters
        ----------
        bit : int
            Bit a enviar.
        """

        self.send_cable.value = bit

    def receive(self):
        """Lee del cable receptor.

        Returns
        -------
        int
            Bit leído.
        """

        return self.receive_cable.value

    @property
    def send_value(self):
        """int: Bit que se encuentra en el cable de escritura"""
        return self.send_cable.value

    @property
    def receive_value(self):
        """int: Bit que se encuentra en el cable de lectura"""
        return self.receive_cable.value


class Duplex():
    """
    Cable duplex.

    Parameters
    ----------
    simple : bool, optional
        Especifíca si el cable es tratado como un cable simple, o sea,
        si el cable de lectura y escritura serán el mismo, por defecto en
        ``False``.
    """

    def __init__(self, simple=False):
        cable_1 = Cable()
        cable_2 = Cable() if not simple else cable_1
        self._head_1 = DuplexCableHead(cable_1, cable_2)
        self._head_2 = DuplexCableHead(cable_2, cable_1)

    @property
    def head_1(self):
        """DuplexCableHead: Extremo 1 del cable"""
        return self._head_1

    @property
    def head_2(self):
        """DuplexCableHead: Extremo 2 del cable"""
        return self._head_2
