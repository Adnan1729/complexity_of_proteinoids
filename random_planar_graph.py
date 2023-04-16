import networkx as nx
import random
import matplotlib.pyplot as plt

def is_planar(G):
    try:
        nx.check_planarity(G)
        return True
    except nx.NetworkXException:
        return False

def random_planar_graph(min_nodes, max_nodes):
    n = random.randint(min_nodes, max_nodes)
    G = nx.Graph()

    G.add_nodes_from(range(n))

    while True:
        a = random.choice(list(G.nodes))
        b = random.choice(list(G.nodes))
        if a != b and not G.has_edge(a, b):
            G.add_edge(a, b)
            if not is_planar(G):
                G.remove_edge(a, b)

        if len(G.edges) == n * (n - 1) // 2:
            break

    return G

if __name__ == "__main__":
    G = random_planar_graph(5, 15)
    nx.draw(G, with_labels=True)
    plt.show()
