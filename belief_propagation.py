from node import *
from graph_manipulation import *
from itertools import product
from collections import OrderedDict

'''
    Open the input file and read it.
'''
def read_input_file(input_file):
    with open(input_file, "r") as f:
        data = f.readlines()
    return data

'''
    Read the probability to be calculated for a specific line.
    Create two dictionaries with left and right values.
'''
def read_probability(data, line):
    left_values, right_values = {}, {}

    #Split the line in two parts
    left, right = data[line].split("|")
    
    for probability in left.split():
        #Compute each var=val value from the left side
        variable, value = probability.split("=")
        left_values[variable] = value
    
    for probability in right.split():
        #Compute each var=val value from the right side
        variable, value = probability.split("=")
        right_values[variable] = value

    return (left_values, right_values)

'''
    Compute the initial factor for all the cliques.
'''
def compute_factor_cliques(G, maximal_cliques, clique_tree):
    for clique in maximal_cliques:
            #Initialize an empty factor 
            clique_factor = Factor([], [])

            for node in clique:
                if G[node].used_factor == False:
                    #Check if a factor for a specific variable was used

                    #Make sure that all factor variables are in the clique
                    if(len(set(G[node].parents_names).difference(
                        set(clique))) == 0):
                        
                        G[node].used_factor = True
                        
                        #Multiply the initial factor with variable's factor
                        current_factor = G[node].factor
                        clique_factor = factor_operation(clique_factor,
                                current_factor, "*")
            
            #Set the factor for the clique
            clique_tree[tuple(clique)].factor = clique_factor

'''
    dfs_util function for the dfs described below.
'''
def dfs_util(graph, node, visited):
    index = list(graph.keys()).index(tuple(node))
    
    #Mark current node as visited
    visited[index] = True

    for neighbour in graph[tuple(node)].neighbours:
        #Iterate the neighbours of the node
        index = list(graph.keys()).index(tuple(neighbour))

        if not visited[index]:
            #Mark the not visited neighbour as child to the node
            graph[tuple(node)].add_child(neighbour)

            #Set the parent for the neighbour to be the node
            graph[tuple(neighbour)].add_parent(node)

            dfs_util(graph, neighbour, visited)

    #Copmute the common variables between parent and children
    graph[tuple(node)].common_children_prepare()

'''
    Compute dfs on a tree to compute the child-parent relationship.
'''
def dfs(graph):
    visited = [False] * len(graph)

    for index, node in enumerate(graph):
        index = list(graph.keys()).index(node)

        #Check if current node is not visited
        if not visited[index]:
            dfs_util(graph, node, visited)

'''
    Calculate Phi_0 for all the nodes in the tree.
'''
def calculate_factor_0(clique_tree, root, leaf, right_values):
    for node in clique_tree:
        #Calculate Phi_0 for each node
        clique_tree[node].prepare_factor_0(right_values)

        #Save the leaf node and root
        if clique_tree[node].is_leaf():
            leaf.append(node)
        if clique_tree[node].is_root():
            root.append(node)

'''
    Calculate Phi_1 for all the nodes in the tree.
'''
def calculate_factor_1(clique_tree, leaf):
    for val in leaf:
        #Prepare Phi_1 for the leaf
        clique_tree[val].prepare_factor_1()

        #Get the parent of the current node
        parent = clique_tree[val].parent

        while parent != None:
            #Go up till root and prepare Phi_1 for all nodes
            clique_tree[tuple(parent)].prepare_factor_1()
            parent = clique_tree[tuple(parent)].parent

'''
    DFS function for the Phi_u to be calculated.
'''
def dfs_factor_u(graph, node, visited):
    index = list(graph.keys()).index(tuple(node))
    
    #Mark current node as visited
    visited[index] = True

    #Calculate Phi_u for the current node
    graph[tuple(node)].prepare_factor_u()
    for child in graph[tuple(node)].children:
        index = list(graph.keys()).index(tuple(child))

        #Calculate Phi_u for all children
        if visited[index] == False:
            dfs_factor_u(graph, child, visited)

def calculate_factor_u(graph, root):
    visited = [False] * len(graph)

    dfs_factor_u(graph, root, visited)

'''
    Get a clique that contains all the variables in the probability to be
    calculated.
'''
def get_good_factor(clique_tree, left_values):
    good_factor = None
    
    for node in clique_tree:
        contains_all = True

        #Check if clique contains all variables
        for var in left_values:
            if var not in node:        
                contains_all = False
                break

        if contains_all == True:
            #If contains all variable -> clique found
            good_factor = deepcopy(clique_tree[node].factor_u)
            break
    

    return good_factor

'''
    Calculate the final probability from a found factor.
'''
def calculate_final_probability(left_values, good_factor):
    for pair in good_factor.values:
        good_line = True
        
        #Find the line that contains the right values for all variables
        for i in range(0, len(good_factor.variables)):
            var = good_factor.variables[i]

            if int(left_values[var]) != int(pair[i]):
                good_line = False
                break
       
        #Proability found
        if good_line == True:
            return good_factor.values[pair]


def main():
    for input_file in ["bnet-0", "bnet-1", "bnet-2", "bnet-3"]:
        print('Test: ' + input_file)
        #Read the data from file
        data = read_input_file(input_file)
        N, M = [int(x) for x in data[0].split()]
    
        #Copute the initial bayes network graph
        G, nodes_names = build_graph(data, N)
    
        #Compute the undirected graph from th BN
        U = build_undirected_graph(G)
    
        #Moralize the undirected graph
        H = moralize_graph(U)
       
        #Compute the chordal graph
        H_star = build_chordal_graph(H)
    
        #Compute the maximal cliques from the graph
        maximal_cliques = build_maximal_cliques(H_star, nodes_names)
    
        #Build the graph of cliques and the maximal tree out of it
        C = build_graph_of_cliques(maximal_cliques)
        T = kruskal(C, len(maximal_cliques))
    
        #Represent the tree as a graph and compute the factor for all nodes
        clique_tree = graph_from_tree(T)
        compute_factor_cliques(G, maximal_cliques, clique_tree)
    
        #Mark the child-parent relationship inside the graph
        dfs(clique_tree)
    
        #Calculate all the probabilities
        for line in range(N + 1, N + M + 1):
            #Get the values from the left and right for the current probability
            left_values, right_values = read_probability(data, line)
    
            #Save the expected result for the probability
            correct_answer = data[N + M + 1 + (line - N - 1)]
        
            leaf = []
            root = []
            
            #Calculate Phi_0 for all nodes in graph
            calculate_factor_0(clique_tree, root, leaf, right_values)
            root = root[0]
    
            #Calculate Phi_1 for all nodes in graph
            calculate_factor_1(clique_tree, leaf)
           
            #Calculate Phi_u for all node in graph
            calculate_factor_u(clique_tree, root)
    
            #Find a clique that contains all vars from probability
            good_factor = get_good_factor(clique_tree, left_values)
    
            if not good_factor:
                #Create a new factor having variables from separate cliques
                good_factor = factor_from_separate_cliques(clique_tree, root,
                        left_values)
                print("BONUS")
    
            #Compute the final probability to be printed
            good_factor = normalize_factor(good_factor, left_values) 
            probability = calculate_final_probability(left_values, good_factor)
            
            print(data[line])
            print(f"Own probability = {probability:.7f}")
            print(f"Ref probability = {correct_answer}")
            print('-' * 50)

if __name__ == "__main__":
    main()
