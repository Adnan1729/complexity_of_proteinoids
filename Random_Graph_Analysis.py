import numpy as np
import networkx as nx
import random
from scipy.spatial import Delaunay
import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Inches

##
def random_points(min_nodes, max_nodes, scale=1200):
    n = random.randint(min_nodes, max_nodes)
    points = np.random.rand(n, 2) * scale
    return points

##
def delaunay_triangulation(points):
    tri = Delaunay(points)
    G = nx.Graph()
    
    for i, point in enumerate(points):
        G.add_node(i, pos=point)
    
    for simplex in tri.simplices:
        u, v, w = simplex
        u_coord, v_coord, w_coord = points[u], points[v], points[w]
        G.add_edge(u, v, weight=np.linalg.norm(u_coord - v_coord))
        G.add_edge(v, w, weight=np.linalg.norm(v_coord - w_coord))
        G.add_edge(w, u, weight=np.linalg.norm(w_coord - u_coord))
    
    return G, points

##
def remove_random_edges(G, p=0.1):
    num_edges = len(G.edges())
    num_to_remove = int(num_edges * p)
    
    edges = list(G.edges())
    random.shuffle(edges)
    
    for edge in edges[:num_to_remove]:
        G.remove_edge(*edge)
        
    return G

##
def percolation_threshold(G):
    if nx.is_connected(G):
        return 1.0
    else:
        largest_cc = max(nx.connected_components(G), key=len)
        return len(largest_cc) / G.number_of_nodes()

##    
def process_data(G, pos, points):
    perc_threshold = percolation_threshold(G)

    if not nx.is_connected(G):
        Gcc = sorted(nx.connected_components(G), key=len, reverse=True)
        G = G.subgraph(Gcc[0])
    all_pairs_shortest_paths = nx.algorithms.shortest_paths.floyd_warshall_numpy(G)

    total_effective_resistance = 0
    for i, u in enumerate(G.nodes):
        for j, v in enumerate(G.nodes):
            if i < j:
                shortest_path_length = all_pairs_shortest_paths[i][j]
                effective_resistance = 1 / shortest_path_length
                total_effective_resistance += effective_resistance

    total_shortest_paths = sum([sum(row) for row in all_pairs_shortest_paths])
    average_shortest_path = total_shortest_paths / (len(G.nodes) * (len(G.nodes) - 1))

    total_edge_lengths = sum([G.edges[edge]['weight'] for edge in G.edges])
    average_edge_length = total_edge_lengths / len(G.edges)

    nx.draw_networkx_nodes(G, pos, node_size=15)
    nx.draw_networkx_edges(G, pos)
    graph_filename = f'graph_{len(G.nodes)}.png'
    plt.savefig(graph_filename)
    plt.close()
    
    print(f"Graph with {len(G.nodes)} nodes")
    print("Total effective resistance=", total_effective_resistance)
    print("Average shortest path=", average_shortest_path)
    print("Average edge length=", average_edge_length)
    print("Percolation threshold=", perc_threshold)
    print()

    return total_effective_resistance, average_shortest_path, average_edge_length, perc_threshold

##
import seaborn as sns
import pandas as pd

def run_simulation(num_iterations, p_values):
    # Prepare a dataframe to store the results for each p
    df = pd.DataFrame(columns=['p', 'total_eff_resistance', 'avg_shortest_path', 'avg_edge_length', 'perc_threshold', 'iteration'])

    for i in range(num_iterations):
        for p in p_values:
            points = random_points(90, 100)
            G, pos = delaunay_triangulation(points)
            G = remove_random_edges(G, p=p)
            total_eff_resistance, avg_shortest_path, avg_edge_length, perc_threshold = process_data(G, pos, points)

            # Append the results to the dataframe
            new_row = pd.DataFrame({
                'p': [p],
                'total_eff_resistance': [total_eff_resistance],
                'avg_shortest_path': [avg_shortest_path],
                'avg_edge_length': [avg_edge_length],
                'perc_threshold': [perc_threshold],
                'iteration': [i]  # Add iteration number as a new column
            })
            df = pd.concat([df, new_row], ignore_index=True)

    # Plot the results
    fig, axs = plt.subplots(2, 2, figsize=(12, 10))

    properties = ['total_eff_resistance', 'avg_shortest_path', 'avg_edge_length', 'perc_threshold']
    colors = ['blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black', 'white', 
              'orange', 'purple', 'pink', 'brown', 'gray', 'olive', 'lime', 'teal', 'gold', 'navy', 'maroon', 'silver']


    for i, col in enumerate(properties):
        for j in range(num_iterations):
            sns.regplot(x='p', y=col, data=df[df['iteration']==j], scatter_kws={'s': 10}, lowess=True, ax=axs[i//2, i%2], color=colors[j])
        axs[i//2, i%2].set_title(f'{col} vs p')

    plt.tight_layout()
    plt.show()




if __name__ == "__main__":
    num_iterations = 19  # Define the number of iterations here
    p_values = np.linspace(0.5, 0.9, 10)  # Define the range of p values here
    run_simulation(num_iterations, p_values)
