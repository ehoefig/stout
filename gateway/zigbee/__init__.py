import binascii

__author__ = 'edzard'


# TODO: implement repr()
class Address:

    def __init__(self, short, long):
        self.short, self.long = short, long

    def __str__(self):
        return "{} ({})".format(binascii.hexlify(self.short).decode().upper(),binascii.hexlify(self.long).decode().upper())

    def __eq__(self, other):
        return other and self.short == other.short and self.long == other.long

    def __hash__(self):
        return hash(self.short) ^ hash(self.long)