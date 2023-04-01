import math


class Ipv4FormatError(Exception):
    def __init__(self, message="O endereço Ipv4 fornecido não está no formato a.b.c.d"):
        self.message = message
    pass


class NetworkFormatError(Exception):
    def __init__(self, message="A representação da rede fornecida não está no formato a.b.c.d/x"):
        self.message = message
    pass


class Ipv4Address:
    MASK_OCTET1 = int(math.pow(2, 8)) - 1
    OCTET4_SHIFT_AMOUNT = 24
    OCTET3_SHIFT_AMOUNT = 16
    OCTET2_SHIFT_AMOUNT = 8
    IPV4_TOTAL_BITS = 32
    IPV4_TOTAL_BYTES = 4

    def __init__(self, ip_address):
        self.ip_address = ip_address

    def __and__(self, other):
        if isinstance(other, int):
            return Ipv4Address(self.ip_address & other)
        if isinstance(other, Ipv4Address):
            return Ipv4Address(self.ip_address & other.ip_address)

        raise TypeError("Não é possível realizar uma operação AND entre Ipv4Address e {}".format(type(other)))

    def __or__(self, other):
        if isinstance(other, int):
            return Ipv4Address(self.ip_address | other)
        if isinstance(other, Ipv4Address):
            return Ipv4Address(self.ip_address | other.ip_address)

        raise TypeError("Não é possível realizar uma operação OR entre Ipv4Address e {}".format(type(other)))

    def __add__(self, other):
        if isinstance(other, int):
            return Ipv4Address(self.ip_address + other)
        if isinstance(other, Ipv4Address):
            return Ipv4Address(self.ip_address + other.ip_address)

        raise TypeError("Não é possível realizar uma operação ADD entre Ipv4Address e {}".format(type(other)))

    def __eq__(self, other):
        return self.ip_address == other.ip_address

    def __gt__(self, other):
        return self.ip_address > other.ip_address

    def __ge__(self, other):
        return self.ip_address >= other.ip_address

    def __lt__(self, other):
        return self.ip_address < other.ip_address

    def __le__(self, other):
        return self.ip_address <= other.ip_address

    def __str__(self):
        return self.getStrRepresentation()

    def getStrRepresentation(self):
        octet1 = self.ip_address & Ipv4Address.MASK_OCTET1
        octet2 = (self.ip_address >> Ipv4Address.OCTET2_SHIFT_AMOUNT) & Ipv4Address.MASK_OCTET1
        octet3 = (self.ip_address >> Ipv4Address.OCTET3_SHIFT_AMOUNT) & Ipv4Address.MASK_OCTET1
        octet4 = (self.ip_address >> Ipv4Address.OCTET4_SHIFT_AMOUNT) & Ipv4Address.MASK_OCTET1

        return "{}.{}.{}.{}".format(octet4, octet3, octet2, octet1)

    @staticmethod
    def ipv4StrToDecimal(str_ipv4):
        octets = str_ipv4.split('.')
        ip_decimal = 0
        if len(octets) != Ipv4Address.IPV4_TOTAL_BYTES:
            raise Ipv4FormatError()
        for i in range(0, Ipv4Address.IPV4_TOTAL_BYTES):
            ip_decimal = ip_decimal | (int(octets[i]) << (3 - i) * 8)

        return ip_decimal

    @staticmethod
    def fromStrIpv4(str_ipv4):
        return Ipv4Address(Ipv4Address.ipv4StrToDecimal(str_ipv4))


class Network:

    def __init__(self, ipv4_address, cidr):
        self.ipv4_address = ipv4_address
        self.cidr = cidr

    def __str__(self):
        return "{}/{}".format(self.ipv4_address, self.cidr)
    
    @classmethod
    def fromNetworkStr(cls, prefix):
        if len(prefix.split('/')) != 2:
            raise NetworkFormatError()
        network_address = Ipv4Address.fromStrIpv4(prefix.split('/')[0])
        network_cidr = int(prefix.split('/')[1])

        return cls(network_address, network_cidr)

    def getNetworkAddress(self):
        mask = -1 << (Ipv4Address.IPV4_TOTAL_BITS - self.cidr)
        return self.ipv4_address & mask

    def getBroadcastAddress(self):
        mask = int(math.pow(2, Ipv4Address.IPV4_TOTAL_BITS - self.cidr) - 1)
        return self.ipv4_address | mask
    
    def isNetworkPrefix(self):
        return self.ipv4_address == self.getNetworkAddress()

    def containsIpv4(self, ipv4_address):
        network_address = self.getNetworkAddress()
        broadcast_address = self.getBroadcastAddress()
        return network_address <= ipv4_address <= broadcast_address

    def getTotalIpsInNetwork(self):
        host_number_bits = Ipv4Address.IPV4_TOTAL_BITS - self.cidr
        return int(math.pow(2, host_number_bits))

    def getTotalAlocatableIpsInNetwork(self):
        return self.getTotalIpsInNetwork() - 2

