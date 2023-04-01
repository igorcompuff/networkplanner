from network import Ipv4Address, Network
import math


class ImpossibleSubnetAllocationError(Exception):
    def __init__(self, message="Não é possível realizar as alocações com os requisitos solicitados"):
        self.message = message
    pass


class NetworkPlanner:
    def __init__(self, network):
        self.network = network
        self.allocation = []
        self.requirements = []

    def addRequirement(self, subnet_id, total_addresses):
        self.requirements.append((subnet_id, total_addresses))

    def doPlan(self):
        offset_from_network = 0
        self.requirements.sort(key=lambda requirement: requirement[1], reverse=True)
        for requirement in self.requirements:
            subnet_id, required_addresses = requirement
            host_bits = math.ceil(math.log(required_addresses, 2))
            total_hosts = int(math.pow(2, host_bits))
            cidr = Ipv4Address.IPV4_TOTAL_BITS - host_bits

            network_address = self.network.ipv4_address + offset_from_network

            if not self.network.containsIpv4(network_address):
                raise ImpossibleSubnetAllocationError()

            subnet = Network(network_address, cidr)
            self.allocation.append((subnet_id, required_addresses, subnet))
            offset_from_network += total_hosts

    def printNetworkPlan(self):
        self.allocation.sort(key=lambda alloc: alloc[1], reverse=True)
        print("Network: {}\n".format(self.network))
        for subnet_allocation in self.allocation:
            subnet_id, required_addresses, subnet = subnet_allocation
            print("Subnet Id: {}\tEndereços requeridos: {}\tSubrede: {}\n".format(subnet_id, required_addresses, subnet))