import random
import math
from network import Network, Ipv4Address, NetworkPlanner

class IpAllocationQuestion:
    MIN_SUBNETS_PER_ITEM = 3
    MAX_SUBNETS_PER_ITEM = 5
    MIN_NETWORK_MASK = 20
    MAX_NETWORK_MASK = 26
    MAX_USEFULL_MASK = 29
    MAX_DENOMINATOR = 10
    MAX_EXTRA_ADDRESSES = 10

    def __init__(self):
        self.items = []
        self.createQuestion()
    
    def createRandomNetwork(self):
        ipv4_address = Ipv4Address(random.getrandbits(Ipv4Address.IPV4_TOTAL_BITS))
        network_mask = random.randint(self.MIN_NETWORK_MASK, self.MAX_NETWORK_MASK)
        return Network(ipv4_address, network_mask)

    def getRandomMasks(self, network, total_subnets):
        masks = []
        mask_min_offset = int(math.ceil(math.log2(total_subnets)))
        total_allocated_addresses = 0
        while len(masks) < total_subnets:
            subnet_mask = random.randint(network.mask + mask_min_offset, self.MAX_USEFULL_MASK)
            total_subnet_addressses = Network(mask=subnet_mask).getTotalAddresses()
            total_addresses = total_subnet_addressses + total_allocated_addresses
            if total_addresses < network.getTotalAddresses() or \
                ((total_addresses == network.getTotalAddresses()) and (total_subnets - len(masks)) == 1):
                total_allocated_addresses = total_addresses
                masks.append(subnet_mask)
        return masks

    
    def addItem(self, allocation_possible=True):
        network = self.createRandomNetwork()
        total_subnets = random.randint(self.MIN_SUBNETS_PER_ITEM, self.MAX_SUBNETS_PER_ITEM)
        subnet_masks = self.getRandomMasks(network, total_subnets)
        item = {network: []}
        for subnet_mask in subnet_masks:
            subnet_size = Network(mask=subnet_mask).getTotalAllocatableAddresses()
            requirement = random.randint(subnet_size/2, subnet_size)
            item[network].append(requirement)
        if not allocation_possible:
            total_requirement = sum(item[network])
            remaining_addresses = network.getTotalAllocatableAddresses() - total_requirement
            additional_address_share = (remaining_addresses // total_subnets) + random.randint(1, self.MAX_EXTRA_ADDRESSES)
            item[network] = list(map(lambda requirement: requirement + additional_address_share, item[network]))
        
        self.items.append(item)
    
    def createQuestion(self):
        impossible_alloc_item = random.randint(1, 3)
        for i in range(1, 4):
            self.addItem(allocation_possible=(i != impossible_alloc_item))
    
    def printQuestion(self):
        net_id = 1
        for item in self.items:
            network, requirements = list(item.items())[0]
            print("R{}: {}\n".format(net_id, network))
            subnet_id = 1
            for requirement in requirements:
                print("R{}{}: {} Estações".format(net_id, subnet_id, requirement))
                subnet_id += 1
            net_id += 1
            print("\n")
    
    def printAnswer(self):
        net_id = 1
        for item in self.items:
            network, requirements = list(item.items())[0]
            network_planner = NetworkPlanner(network)
            subnet_id = 1
            for requirement in requirements:
                network_planner.addRequirement("R{}{}".format(net_id, subnet_id), requirement)
                subnet_id += 1
            net_id += 1
            network_planner.doPlan()
            network_planner.printNetworkPlan()
            
            print("\n")

question = IpAllocationQuestion()
question.printQuestion()
question.printAnswer()
        