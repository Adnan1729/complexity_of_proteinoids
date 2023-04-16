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
        u = random.choice(list(G.nodes))
        v = random.choice(list(G.nodes))
        if u != v and not G.has_edge(u, v):
            G.add_edge(u, v)
            if not is_planar(G):
                G.remove_edge(u, v)

        if len(G.edges) == n * (n - 1) // 2:
            break

    return G

if __name__ == "__main__":
    G = random_planar_graph(5, 15)
    nx.draw(G, with_labels=True)
    plt.show()
