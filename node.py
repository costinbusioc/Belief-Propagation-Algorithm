from copy import deepcopy
from factor import *
from collections import OrderedDict

'''
    Representation of a variable inside the graphs that will be used.
'''
class Node:
    def __init__ (self, name, parents_names = [], probabilities = []):
        self.name = name
        self.parents_names = deepcopy(parents_names)
        self.probabilities = deepcopy(probabilities)

        self.children_names = []
        self.neighbours_names = deepcopy(parents_names)

        # Reference to the Node object of all neighbours
        self.neighbours = []

        #The initial factor for each variable
        self.factor = Factor([name] + parents_names, probabilities,
                OrderedDict())

        #Boolean to check if the factor of the variable was used for a clique
        self.used_factor = False

    #Add the name of a parent
    def add_parent_name(self, parent):
        self.parents_names.append(parent)
        self.neighbours_names.append(parent)

    #Add the name of a child
    def add_child_name(self, child):
        self.children_names.append(child)
        self.neighbours_names.append(child)

    #Add the name of a neighbour
    def add_neighbour_name(self, neighbour):
        self.neighbours_names.append(neighbour)

    #Add the reference node of a neighbour
    def add_neighbour(self, neighbour):
        self.neighbours.append(neighbour)

    #Removing a neighbour
    def remove_neighbour(self, neighbour_name):
        index = self.neighbours_names.index(neighbour_name)

        self.neighbours.pop(index)
        self.neighbours_names.pop(index)

    #Return a list with the unconnected parents of a node
    def unconnected_neighbours_names(self):
        unconnected = []

        nr_neighbours_names = len(self.neighbours_names)
        for i in range(0, nr_neighbours_names - 1):
            for j in range(i + 1, nr_neighbours_names):

                neighbours_names_i = self.neighbours[i].neighbours_names
                if self.neighbours_names[j] not in neighbours_names_i:
                    unconnected.append((self.neighbours_names[i],
                        self.neighbours_names[j]))

        return (self.name, unconnected)

    def print_node(self):
        print("Node name is"),(self.name)
        print("parents_names are"),(self.parents_names)
        print("Probabilities are"),(self.probabilities)
        print("children_names are"),(self.children_names)
        print("neighbours_names are"),(self.neighbours_names)
