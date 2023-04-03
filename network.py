import math, functools


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

    def __init__(self, ipv4_address=0, mask=0):
        self.ipv4_address = ipv4_address
        self.mask = mask

    def __str__(self):
        return "{}/{}".format(self.ipv4_address, self.mask)
    
    @classmethod
    def fromNetworkStr(cls, network_str):
        if len(network_str.split('/')) != 2:
            raise NetworkFormatError()
        network_address = Ipv4Address.fromStrIpv4(network_str.split('/')[0])
        network_mask = int(network_str.split('/')[1])

        return cls(network_address, network_mask)

    def getNetworkAddress(self):
        mask = -1 << (Ipv4Address.IPV4_TOTAL_BITS - self.mask)
        return self.ipv4_address & mask

    def getBroadcastAddress(self):
        mask = int(math.pow(2, Ipv4Address.IPV4_TOTAL_BITS - self.mask) - 1)
        return self.ipv4_address | mask
    
    def isNetworkPrefix(self):
        return self.ipv4_address == self.getNetworkAddress()

    def containsIpv4(self, ipv4_address):
        network_address = self.getNetworkAddress()
        broadcast_address = self.getBroadcastAddress()
        return network_address <= ipv4_address <= broadcast_address
    
    def getTotalAddresses(self):
        host_number_bits = Ipv4Address.IPV4_TOTAL_BITS - self.mask
        return int(math.pow(2, host_number_bits))
    
    def getTotalAllocatableAddresses(self):
        return self.getTotalAddresses() - 2


class NetworkPlanner:
    def __init__(self, network):
        self.network = network
        self.allocation = []
        self.requirements = []

    def addRequirement(self, subnet_id, total_addresses):
        self.requirements.append((subnet_id, total_addresses))

    def doPlan(self):
        
        total_requirements = sum(list(map(lambda requirement: requirement[1], self.requirements)))
        
        if self.network.getTotalAllocatableAddresses() >= total_requirements:
            offset_from_network = 0
            self.requirements.sort(key=lambda requirement: requirement[1], reverse=True)
            network_address = self.network.getNetworkAddress()
            for requirement in self.requirements:
                subnet_id, required_addresses = requirement
                host_bits = math.ceil(math.log(required_addresses, 2))
                total_hosts = int(math.pow(2, host_bits))
                mask = Ipv4Address.IPV4_TOTAL_BITS - host_bits
                subnet_address = network_address + offset_from_network
                subnet = Network(subnet_address, mask)
                self.allocation.append((subnet_id, required_addresses, subnet))
                offset_from_network += total_hosts

    def printNetworkPlan(self):
        self.allocation.sort(key=lambda alloc: alloc[1], reverse=True)
        print("Network: {}\n".format(self.network))
        if len(self.allocation) > 0:
            for subnet_allocation in self.allocation:
                subnet_id, required_addresses, subnet = subnet_allocation
                print("{}: {} Estações - {}".format(subnet_id, required_addresses, subnet))
        else:
            print("Não é possível realizar as alocações com os requisitos solicitados")