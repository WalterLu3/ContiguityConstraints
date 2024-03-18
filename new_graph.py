import networkx as nx
import matplotlib.pyplot as plt

#G = nx.Graph()

adj = [("a","b"),("b","c"),("c","d"),("d","e"),("e","f"),("f","a"),("a","d")]

nodeWeight = {
    "a":0.5,    
    "b":0.7,
    "c":0.4,
    "d":0.2,
    "e":0.5,
    "f":0.7   
}


nodes = []
for edge in adj:
    nodes.append(edge[0])
    nodes.append(edge[1])

nodes = list(set(nodes))

#create new edges
new_adj = []
for i in nodes:
    new_adj.append((str(i)+"_in" , str(i)+"_out"))

for edge in adj:
    new_adj.append((str(edge[0])+"_out" , str(edge[1])+"_in"))
    new_adj.append((str(edge[1])+"_out" , str(edge[0])+"_in"))

G = nx.DiGraph(new_adj)

for e in G.edges:
    G.edges[e]['capacity'] = 100

for k in nodeWeight:
    G.edges[(str(k)+"_in" , str(k)+"_out")]['capacity']= nodeWeight[k]

cut_value, partition = nx.minimum_cut(G, "b_out", "e_in")
cutset = set()
reachable, non_reachable = partition
for u, nbrs in ((n, G[n]) for n in reachable):
    cutset.update((u, v) for v in nbrs if v in non_reachable)

print(cutset)
nx.draw(G,with_labels = True)
plt.show()
#G.add_edges_from([(1,2),(2,3)])
