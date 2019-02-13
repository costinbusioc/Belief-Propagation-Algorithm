from node import *
from clique_node import *
from collections import OrderedDict

#the maximal cliques computed from graph
maximal_cliques = []

'''
    Compute the graph from the input file.
'''
def build_graph(data, N, M):

    G = {}
    nodes_names = []

    for line in range(1, N + 1):
        #Read current node
        node_data = data[line].split(' ;')
        
        #Node information
        node_name = node_data[0]
        node_parents = [x for x in node_data[1].split()]
        node_probabilities = [float(x) for x in node_data[2].split()]

        #Create a new node object and save in dictionary
        node = Node(node_name, node_parents, node_probabilities)
        G[node_name] = node

        #Save the name of the node in a separate list
        nodes_names.append(node_name)

    #All the nodes created -> add reference to the actual nodes
    for node in G:
        parents_names = G[node].parents_names
        for parent in parents_names:
            #Add reference to all parents
            G[node].add_neighbour(G[parent])

    return (G, nodes_names)

''' 
    Create undirected graph from the BN
'''
def build_undirected_graph(G):
    U = deepcopy(G)
    
    for node in U:
        parents_names = U[node].parents_names
        for parent in parents_names:
            #Add reference to the children in the parents nodes
            U[parent].add_child_name(node)
            U[parent].add_neighbour(U[node])

    return U

'''
    Create edges between parents of the same variable
'''
def moralize_graph(U):
    H = deepcopy(U)

    for node in H:
        
        #Get the parents of the current node
        parents_names = U[node].parents_names
        nr_parents = len(parents_names)

        for i in range(0, nr_parents - 1):
            for j in range(i + 1, nr_parents):
                #Add edge between all parents of the same node
                H[parents_names[i]].add_neighbour_name(
                        parents_names[j])
                H[parents_names[j]].add_neighbour_name(
                        parents_names[i])
                
                H[parents_names[i]].add_neighbour(H[parents_names[j]])
                H[parents_names[j]].add_neighbour(H[parents_names[i]])
    return H

'''
    Build the chordal graph from a graph.
'''
def build_chordal_graph(H):

    H_star = deepcopy(H)
    
    #Graph to be manipulated to check which node to remove next
    H_copy = deepcopy(H)

    while 1:

        #Get the unconnected list of parents for all nodes
        unconnected = [H_copy[node].unconnected_neighbours_names() 
                for node in H_copy]
        #Sort the unconnected list by the number of unconnected parents
        unconnected.sort(key=lambda elem: (len(elem[1]), elem[0]))
        
        #Check if current representation is already a clique
        last = unconnected[-1]
        if (len(last[1]) == 0):
            break

        #Get the current node to remove and connect its parents
        name_to_delete, pairs = unconnected[0]
        neigh_names = H_copy[name_to_delete].neighbours_names
        
        #Remove the current node from the graph
        for name in neigh_names:
            H_copy[name].remove_neighbour(name_to_delete)
        H_copy.pop(name_to_delete)

        #Connect the pair of neighbours
        for pair in pairs:
            first, second = pair

            #Connect them in the copy graph
            H_copy[first].add_neighbour_name(second)
            H_copy[first].add_neighbour(H_copy[second])

            H_copy[second].add_neighbour_name(first)
            H_copy[second].add_neighbour(H_copy[first])

            H_star[first].add_neighbour_name(second)
            H_star[first].add_neighbour(H_star[second])

            #Connect them in the H_star
            H_star[second].add_neighbour_name(first)
            H_star[second].add_neighbour(H_star[first])

    return H_star

'''
    Implementantion of Bronk Kerbosch 1 algorithm.
'''
def bronk_kerbosch1(R, P, X, H_star):
    if len(P) == 0 and len(X) == 0:
        #Sort the nodes in the clique
        R.sort()
        maximal_cliques.append(R)
        return

    for node in P[:]:
        #Get the neighbours of the current node
        neighbours = H_star[node].neighbours_names

        next_P = list(set(P).intersection(set(neighbours)))
        next_X = list(set(X).intersection(set(neighbours)))

        bronk_kerbosch1(R + [node], next_P, next_X, H_star)
        P.remove(node)
        X.append(node)

'''
    Build the maximal_cliques by applying the bronk kerbosch 1 algorithm.
'''
def build_maximal_cliques(H_star, nodes_names):
    bronk_kerbosch1([], deepcopy(nodes_names), [], H_star)
    
    return maximal_cliques

'''
    Compute the graph of cliques by computing their edges.
'''
def build_graph_of_cliques(maximal_cliques):
    C = []

    nr_cliques = len(maximal_cliques)

    #Check the connectivity between all cliques
    for i in range(nr_cliques - 1):
        for j in range(i + 1, nr_cliques):
            intersection = len(list(set(maximal_cliques[i]).intersection(
                set(maximal_cliques[j]))))

            if intersection > 0:
                #Intersection means an edge between the two nodes
                C.append((maximal_cliques[i],
                    maximal_cliques[j], intersection))

    #Sort the graph by the number of connectivity variables
    C.sort(key = lambda node: node[2], reverse = True)
    
    return C

'''
    Find the set from current Kruskal sets that contain a specific node.
'''
def find_set(sets, node):
    for i in range(len(sets)):
        for node_set in sets[i]:
            #Get the intersection of a specific node and all nodes
            intersect = list(set(node_set).intersection(node))

            #Check that this node is the one actually looked for
            if len(intersect) == len(node):
                return i

'''
    Compute the union between 2 Kruskal sets.
'''
def union(sets, index1, index2):
    sets[index1] += sets[index2]
    sets.pop(index2)

def kruskal(C, size_tree):
    #Create a set for each node
    sets = [[node] for node in maximal_cliques]

    #Count the number of added edges in the tree
    nr_tree_edges = 0

    T = []

    for i in range(len(C)):
        #Check that the tree is ready
        if nr_tree_edges == size_tree:
            break
        
        #Get the current edge to be added
        first, second, weight = C[i]

        #Compute the set indexes for the two nodes
        index1 = find_set(sets, first)
        index2 = find_set(sets, second)

        if index1 != index2:
            #If nodes are in differente sets -> connect them
            T.append(C[i])
            union(sets, index1, index2)
            nr_tree_edges += 1
    
    return T

'''
    Compute a graph from the tree returned by Kruskal for child-parent relation.
'''
def graph_from_tree(T):
    #Compute an ordered dictionary to represent the graph
    CliqueTree = OrderedDict()

    for edge in T:
        first, second, _ = edge

        #Create a clique_tree node for every node inside the tree
        if tuple(first) not in CliqueTree:
            CliqueTree[tuple(first)] = CliqueNode(first)

        if tuple(second) not in CliqueTree:
            CliqueTree[tuple(second)] = CliqueNode(second)

        #Add neighbour relationship between the two nodes
        CliqueTree[tuple(first)].add_neighbour(second,
                CliqueTree[tuple(second)])
        CliqueTree[tuple(second)].add_neighbour(first,
                CliqueTree[tuple(first)])

    return CliqueTree

'''
    Check if accumulator of clique nodes contains specific variables.
'''
def contains_all(accumulator, left_values):
    for var in left_values:
        contains = False

        for node in accumulator:
            if var in node:
                contains = True
                break

        if contains == False:
            return False

    return True

'''
    DFS util function for creating a subtree.
'''
def dfs_util_subtree(clique_tree, node, visited, accumulator, left_values):
    accumulator += [tuple(node)]
    
    index = clique_tree.keys().index(tuple(node))
    visited[index] = True

    for child in clique_tree[tuple(node)].children:
        if contains_all(accumulator, left_values):
            return
    
        index = clique_tree.keys().index(tuple(child))

        #Calculate Phi_u for all children
        if visited[index] == False:
            dfs_util_subtree(clique_tree, child, visited, accumulator,left_values)

'''
    DFS function to compute a subtree that contains specific variables.
'''
def dfs_subtree(clique_tree, root, accumulator, left_values):
    visited = [False] * len(clique_tree)

    dfs_util_subtree(clique_tree, root, visited, accumulator, left_values)

'''
    Creating a subtree that contains specific variables.
'''
def create_subtree(clique_tree, root, left_values):
    clique_tree_prime = deepcopy(clique_tree)

    accumulator = []
    dfs_subtree(clique_tree_prime, root, accumulator, left_values)

    all_nodes = [tuple(node) for node in clique_tree]
    to_remove = list(set(all_nodes) - (set(accumulator)))

    for remove in to_remove:
        for node in clique_tree_prime:
            clique_tree_prime[node].delete_neighbour(remove)

        clique_tree_prime.pop(remove)

    return clique_tree_prime

'''
    Create a factor for probabilities from separate cliques.
'''
def factor_from_separate_cliques(clique_tree, root, left_values):
    #Create the subtree
    clique_tree_prime = create_subtree(clique_tree, root, left_values)

    good_factor = deepcopy(clique_tree_prime[root].factor_u)

    for node in clique_tree_prime:
        if node != root:
            #Compute the new factor
            clique_tree_prime[node].prepare_factor_r()
            
            #Add the new factor to the current one
            good_factor = factor_operation(good_factor,
                    clique_tree_prime[node].factor_r, "*")

    return good_factor
