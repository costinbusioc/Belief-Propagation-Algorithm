from copy import deepcopy
from collections import OrderedDict
from itertools import product

'''
    Class representing a factor.
'''
class Factor:
    def __init__ (self, variables, probabilities, values = OrderedDict()):
        self.variables = variables
        self.values = values

        if len(values) == 0 and len(probabilities) > 0:
            #Calculate the initial factor for a variable from probabilities
            self.calculate_values(probabilities)

    def calculate_values(self, probabilities):
        nr_variables = len(self.variables)

        #Calculate all arrangements of [0,1] for all variables
        pairs = list(product([0,1], repeat=nr_variables))

        for i in range(0, len(pairs)):
            if i < len(pairs) / 2:
                #First half represents the !variable probability
                self.values[pairs[i]] = 1 - probabilities[i]
            else:
                #Second half is the actual probability received at initalization
                self.values[pairs[i]] = probabilities[i -
                        len(pairs) / 2]

    #Check if a factor is empty
    def empty_factor(self):
        if (len(self.variables) == 0):
            return True
        return False

    #Calculate the index of a variable inside the factor
    def variable_position(self, var):
        if var in self.variables:
            return self.variables.index(var)
        return -1

    #Print a factor
    def print_factor(self):
        if self.empty_factor():
            print("Empty factor")
            return
        
        indent = "\t"

        line = " | ".join(self.variables + ["(" + ",".join(self.variables) + ")"])
        sep = "".join(["+" if c == "|" else "-" for c in list(line)])
        print(indent + sep)
        print(indent + line)
        print(indent +sep)
        for values, p in self.values.items():
            print(indent + " | ".join([str(v) for v in values] + [str(p)]))
        print(indent + sep)

#Calculate a multiply/division operation between two factors
def factor_operation(factor1, factor2, operation = "*"):
    #Check for an empty factor
    if factor1.empty_factor():
        return deepcopy(factor2)
    elif factor2.empty_factor():
        return deepcopy(factor1)

    #The result variables/values
    factor_variables = []
    factor_values = OrderedDict()

    #Compute the new variables for the result factor
    for var in factor1.variables:
        factor_variables.append(var);
    for var in factor2.variables:
        if var not in factor1.variables:
            factor_variables.append(var)
            
    for pair1 in factor1.values:
        for pair2 in factor2.values:
            join = True
            result_pair = []
            
            for var in factor_variables:
                pos1 = factor1.variable_position(var)
                pos2 = factor2.variable_position(var)
                
                #Check that same variable has the same value in both factors
                if pos1 != -1 and pos2 != -1 and pair1[pos1] != pair2[pos2]:
                    join = False
            
            if join:
                #Add the value for each variable
                for var in factor_variables:
                    if var in factor1.variables:
                        pos1 = factor1.variable_position(var)
                        result_pair.append(pair1[pos1])
                    else:
                        pos2 = factor2.variable_position(var)
                        result_pair.append(pair2[pos2])

                #Calculate the final result for a specific configuration
                if operation == "*":
                    factor_values[tuple(result_pair)] = factor1.values[pair1] * factor2.values[pair2]
                elif operation == "/":
                    factor_values[tuple(result_pair)] = factor1.values[pair1] / factor2.values[pair2]

    return Factor(factor_variables, [], factor_values)

#Remove entries that don't respect specific value for a variable
def condition_factors(factor, var, val):
    #Variables will be the same
    respected_variables = deepcopy(factor.variables)
    
    #Keep only specific values
    respected_values = OrderedDict()

    if var in factor.variables:
        index = factor.variables.index(var)
        
        for pair in factor.values:
            #Check that current pair respects the value for the variable
            if int(pair[index]) == int(val):
                respected_values[pair] = factor.values[pair]
        
        return Factor(respected_variables, [], respected_values)
    else:
        return factor

#Remove a variable from a factor by suming out values
def sum_out(var, factor):
    factor_variables = []
    factor_values = OrderedDict()
    
    for variable in factor.variables:
        #Compute the new variables
        if variable != var:
            factor_variables.append(variable)
    
    for pair in factor.values:
        new_pair = []
        for i in range(len(pair)):
            #Keep only the other variables' values
            if i != factor.variables.index(var):
                new_pair.append(pair[i])
        
        #Compute the sum of the same pairs on var = 1 and 0
        if tuple(new_pair) in factor_values:
            factor_values[tuple(new_pair)] += factor.values[pair]
        else:
            factor_values[tuple(new_pair)] = factor.values[pair]
    
    return Factor(factor_variables, [], factor_values)

#Normalize factor on specific variables
def normalize_factor(factor, variables):

    #Remove the variables that should not be in the final factor
    for var in factor.variables:
        if var not in variables:
            factor = sum_out(var, factor)

    #Compute the sum of the factor's values
    sum_factor = 0
    for val in factor.values:
        sum_factor += factor.values[val]

    #Normalize factor
    for val in factor.values:
        factor.values[val] /= sum_factor

    return factor
