# Title: Morphological and functional complexity of proteinoid microspheres ensembles

**Overview**

This code calculates the effective resistance, average shortest path, and average edge length 
of a graph using the NetworkX library in Python.

[4] At the core, all-pairs shortest paths is calculated using Floyd-Warshall algorithm. 
The main idea behind the Floyd-Warshall algorithm is to gradually improve the shortest 
path estimates between all pairs of nodes by considering intermediate nodes (). 
Initially, the algorithm considers the direct edge weights between nodes as the shortest 
path estimates. Then, it iteratively updates the estimates by considering all possible intermediate nodes.

[4.1] For each pair of nodes, the shortest path length is extracted from the all-pairs 
shortest paths array. Then the effective resistance is calculated as  1/(shortest path length). 
The total effective resistance is the sum of all effective resistances.

[4.2] total shortest paths is calculated as the sum of all the shortest path lengths in the all-pairs shortest paths array. 
The average shortest path is then calculated by dividing the total shortest paths by the number of possible pairs of nodes in the graph.
[4.3] The code iterates through all the edges in the graph and sums their weights (lengths) as total edge lengths. 
The average edge length is calculated by dividing the total edge lengths by the number of edges in the graph.

**Input Data Processing**

<img width="212" alt="Screenshot 2023-03-31 114409" src="https://user-images.githubusercontent.com/70011012/229099649-b4c24c91-798b-40d6-8f29-c0645334f804.png">

The xi, yi coordinates and the name of the picture should be laid in the way mentioned above.  

Reference: 

