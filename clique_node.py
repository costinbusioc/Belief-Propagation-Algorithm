from copy import deepcopy
from factor import *

'''
    Class that will represent a node inside the clique graph/tree.
'''
class CliqueNode:
    def __init__(self, name):
        self.name = name

        self.parent = None
        self.children = []
        self.neighbours = []

        #The factors used along the algoirthm
        self.factor = None
        self.factor_0 = None
        self.factor_1 = None
        self.factor_u = None

        #Sent and received factors in propagation process
        self.sent_factor = None
        self.received_factor = None

        #Factor for calculating the bonus
        self.factor_r = None

        #Reference to the actual neighbours
        self.neighbours_nodes = []

        #Common variables between parent and current node
        self.common_parent = None

        #Common variables between children and current node
        self.common_children = []

    def add_neighbour(self, neighbour, node):
        self.neighbours.append(neighbour)
        self.neighbours_nodes.append(node)

    def add_child(self, child):
        self.children.append(child)
  
    def add_parent(self, parent):
        self.parent = parent

        #Caclulate the intersection between parent and node
        self.common_parent = list(set(self.name).intersection(set(parent)))

    def delete_neighbour(self, node):
        if node in self.neighbours:
            index = self.neighbours.keys().index(tuple(node))
            self.neighbours.pop(index)
            self.neighbours_nodes.pop(index)

        if node in self.children:
            self.children.remove(node)
    
    def common_children_prepare(self):
        #Calculate the intersection between current node and each child
        for child in self.children:
            self.common_children.append(list(set(self.name).intersection(set(child))))

    def print_node(self):
        print("Name is"),(self.name)
        print("Parent"),(self.parent)
        print("Common parent"),(self.common_parent)
        print("Children"),(self.children)
        print("Neighbours"),(self.neighbours)
        
        if self.factor != None:
            self.factor.print_factor()

    def is_leaf(self):
        return len(self.children) == 0

    def is_root(self):
        return self.parent == None

    #Calculate Phi_0 for the current probability according to specific variables
    def prepare_factor_0(self, variables):
        self.factor_0 = deepcopy(self.factor)
        
        #Keep specific values for specific variables
        for var in variables:
            self.factor_0 = condition_factors(self.factor_0, var, variables[var])
           
    #Check that all children have Phi_1 calculated
    def all_children_have_factors(self):
        for child in self.children:
            index = self.neighbours.index(child)
            if self.neighbours_nodes[index].factor_1 == None:
                return False

        return True

    #Calculate Phi_1 for the current probability
    def prepare_factor_1(self):
        if self.all_children_have_factors() == False:
            return
        
        #Initialize with factor_0
        self.factor_1 = deepcopy(self.factor_0)

        #Multiply factor_1 with all factor_1 from children
        for child in self.children:
            index = self.neighbours.index(child)
            
            self.factor_1 = factor_operation(self.factor_1,
                    self.neighbours_nodes[index].factor_1, "*")
        
        #Final factor will be initilized to factor_1
        self.factor_u = deepcopy(self.factor_1)
        
        #Remove the variables uncommon to the parent
        for var in self.factor_1.variables:
            if self.common_parent != None and var not in self.common_parent:
                self.factor_1 = sum_out(var, self.factor_1)

        self.sent_factor = deepcopy(self.factor_1)

    #Calculate Phi_u for the current probability
    def prepare_factor_u(self):
        for i in range(0, len(self.children)):
            index = self.neighbours.index(self.children[i])

            #Compute the division between current Phi_u and child Phi_1
            aux_factor = factor_operation(self.factor_u,
                    self.neighbours_nodes[index].factor_1, "/")

            #Remove the variables uncommon to the child
            for var in aux_factor.variables:
                if var not in self.common_children[i]:
                    aux_factor = sum_out(var, aux_factor)

            #Append the current auxiliar factor to the child Phi_u
            self.neighbours_nodes[index].factor_u = factor_operation(
                    self.neighbours_nodes[index].factor_u, aux_factor, "*")

            self.neighbours_nodes[index].received_factor = aux_factor

    #Function to compute the factor for bonus
    def prepare_factor_r(self):
        aux_factor = factor_operation(self.received_factor, self.sent_factor)
        self.factor_r = factor_operation(self.factor_u, aux_factor, "/")

