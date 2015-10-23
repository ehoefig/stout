import binascii

__author__ = 'edzard'


class ZigBeeAddress:
    """
    Stores a single zigbee address consisting of a 16bit short network address, and a longer 64bit IEEE Mac address.
    """

    def __init__(self, network_address, ieee_address):
        self.network_address, self.mac_address = network_address, ieee_address

    def __str__(self):
        return "{} ({})".format(binascii.hexlify(self.network_address).decode().upper(),binascii.hexlify(self.mac_address).decode().upper())

    def __eq__(self, other):
        return other and self.network_address == other.short and self.mac_address == other.long

    def __hash__(self):
        return hash(self.network_address) ^ hash(self.mac_address)



