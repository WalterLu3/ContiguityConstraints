import sys
import networkx as nx
import gurobipy as gp
from gurobipy import GRB
import pickle as pk


CNT = 0

def EuclieanDistance(A,B):
    return ((A[0]-B[0])**2 + (A[1]-B[1])**2)**(1/2)

def getSecond(temp): #return second element of a tuple
    return temp[1]

#print(len(sys.argv))
if len(sys.argv) < 6:
    print('Usage: hw3-steiner.py adjFile populationFile positionFile popBound districtNum')
    quit()

with open(sys.argv[1],"rb") as f:
    adj = pk.load(f)
with open(sys.argv[2],"rb") as f:
    pop = pk.load(f)
with open(sys.argv[3],"rb") as f:
    pos = pk.load(f)
    
boundRate = float(sys.argv[4])
districtNum = int(sys.argv[5])

file_name = "{}_bound{}_districtNum{}".format(sys.argv[1].split("/")[1],int(boundRate*100),districtNum)
sys.stdout = open("{}_{}.log".format("CUTpreadd",file_name), 'w')


# declare vertices
vertex = list(pop.keys()) 
    
VNum = len(vertex)    
# calculate total population
totalPop = 0 
for v in vertex:
    totalPop += pop[v]

popUpBound = (totalPop/districtNum) * (1 + boundRate)
popLowerBound = (totalPop/districtNum) * (1 - boundRate)
# construct distances
w = {}
for v1 in vertex:
    for v2 in vertex:
        w[v1,v2] = EuclieanDistance(pos[v1],pos[v2])

# construct arcs
arcs = []
for a in adj:
    arcs.append(tuple(a))
    arcs.append((a[1],a[0]))

# construct vertex that are not adjacency to a center
G = nx.Graph()
G.add_edges_from(arcs)


vertexNotAdj = {}

for c in vertex:
    vertexNotAdj[c] = set(vertex) - set([c]) - set(G[c])


##############################################################
########construct graph for finding minimum vertex cut########
##############################################################

new_adj = []
for i in vertex:
    new_adj.append((str(i)+"@in" , str(i)+"@out"))

for edge in arcs:
    new_adj.append((str(edge[0])+"@out" , str(edge[1])+"@in"))
    new_adj.append((str(edge[1])+"@out" , str(edge[0])+"@in"))

GRAPH = nx.DiGraph(new_adj)

for e in GRAPH.edges:
    GRAPH.edges[e]['capacity'] = 10000

m = gp.Model('CUT')

#### Hess model ####

# declare assignment binary variable
#x = m.addVars(vertex,vertex, vtype=GRB.BINARY ,name="x")
x = m.addVars(vertex,vertex, ub=1.0, lb=0.0 ,name="x")

#objective funciton
obj = gp.quicksum( w[i,j] * x[i,j]  
                    for i in vertex for j in vertex )

m.setObjective(obj,GRB.MINIMIZE)

# add constraints
m.addConstrs(
    (gp.quicksum(x[i,j] for j in vertex )  == 1 for i in vertex), "onlyOneAssign")

m.addConstr(
    (gp.quicksum(x[i,i] for i in vertex )  ==  districtNum), "centerChoice")

m.addConstrs(
    (gp.quicksum( pop[i] * x[i,j] for i in vertex) <=  popUpBound * x[j,j] for j in vertex), "popUp")

m.addConstrs(
    ( x[i,j] <= x[j,j] for i in vertex for j in vertex), "popUp")

def vertexSeparatorCutPreAdd(model):
    val = m.getAttr("x", x)
    
    #print(val)
    # sorted the district center
    centerList = []
    for i in vertex:
        centerList.append((i,val[i,i])) 
    centerList = sorted(centerList, reverse=True, key=getSecond)   
    
    # starting to add cuts
    hasAdditionalCuts = False
    
    
    for center in centerList:
        
        c = center[0]
        value = center[1]
        #only add cuts for center that has great Xcc value and  when no cut is added
        if value < ((1/VNum) - 0.000001) and (not hasAdditionalCuts):
            break

        #set graph weight
        for v in vertex:
            GRAPH.edges[(str(v)+"@in" , str(v)+"@out")]['capacity'] = val[v,c]

        U = []
        # only add u if it has great possibility to be assigned to c
        for u in vertexNotAdj[c]:
            if val[u,c] >= (1/VNum) + 0.000001 :
                #print(u)
                U.append(u)
        #print(U)
    
        # for each node in U, solve for minimum vertex cut
        
        for u in U:
            cut_value, partition = nx.minimum_cut(GRAPH, str(c)+"@out", str(u)+"@in")
            # get minimum vertex cut
            cutset = set()
            reachable, non_reachable = partition
            for u1, nbrs in ((n, GRAPH[n]) for n in reachable):
                cutset.update((u1, v) for v in nbrs if v in non_reachable)

            S = []
            for v_temp in cutset:
                S.append(v_temp[0].split("@")[0])
            S = set(S)
            
            # Add cut if the sum of vertex weight is smaller than Xcu
            sumVertex = 0
            for v in S:
                sumVertex += val[v,c]
            
            #print(sumVertex,val[u,c])
            if sumVertex < val[u,c] - 0.000001:
                CNT = CNT + 1
                #print("hey")
                model.addConstr(gp.quicksum(x[v,c]
                                            for v in S) >= x[u,c])
                
m._count = 0
m._vars = x
m._vals = None
m.optimize()
# add cut beforehand
for i in range(10):
   vertexSeparatorCutPreAdd(m)
   if CNT == 0:
       break
   CNT = 0
   m.update()
   m.optimize()

#print("cuts : ",m._count)

def vertexSeparatorCut(model, where):
    if where == GRB.Callback.MIPSOL:
    #     model._vals = model.cbGetSolution(model._vars)


    # elif where == GRB.Callback.MIPNODE and model._vals != None:
    #     val = model._vals
        val = model.cbGetSolution(model._vars)
        
        # sorted the district center
        centerList = []
        for i in vertex:
            centerList.append((i,val[i,i])) 
        centerList = sorted(centerList, reverse=True, key=getSecond)   
        
        # starting to add cuts
        hasAdditionalCuts = False
        
        
        for center in centerList:
            
            c = center[0]
            value = center[1]
            #only add cuts for center that has great Xcc value and  when no cut is added
            if value < ((1/VNum) - 0.000001) and (not hasAdditionalCuts):
                break
            
            #set graph weight
            for v in vertex:
                GRAPH.edges[(str(v)+"@in" , str(v)+"@out")]['capacity'] = val[v,c]

            U = []
            # only add u if it has great possibility to be assigned to c
            for u in vertexNotAdj[c]:
                if val[u,c] >= (1/VNum) + 0.000001 :
                    U.append(u)
            #print(U)
        
            # for each node in U, solve for minimum vertex cut
            
            for u in U:
                cut_value, partition = nx.minimum_cut(GRAPH, str(c)+"@out", str(u)+"@in")
                # get minimum vertex cut
                cutset = set()
                reachable, non_reachable = partition
                for u1, nbrs in ((n, GRAPH[n]) for n in reachable):
                    cutset.update((u1, v) for v in nbrs if v in non_reachable)

                S = []
                for v_temp in cutset:
                    S.append(v_temp[0].split("@")[0])
                S = set(S)
                
                # Add cut if the sum of vertex weight is smaller than Xcu
                sumVertex = 0
                for v in S:
                    sumVertex += val[v,c]
                
                if sumVertex < val[u,c] - 0.000001:
                    #m._count = m._count + 1
                    #print("hey")
                    model.cbLazy(gp.quicksum(model._vars[v,c]
                                             for v in S) >= model._vars[u,c])
                
        model._vals = None
        #print(centerList)


for v1 in vertex:
    for v2 in vertex:
        x[v1,v2].vtype = "B" 

m.Params.LazyConstraints = 1
m.Params.timelimit = 1800.0
m.optimize(vertexSeparatorCut)

        



#print(m.getAttr("x", x))
#
#m.optimize(vertexSeparatorCut)
#m.write("output.sol")

CUTSol = {}
for i in vertex:
    for j in vertex:
        if x[i,j].x >0.5:
                CUTSol[i] = j


with open("{}_{}.pk".format("CUTpreadd",file_name),"wb") as f:
    pk.dump(CUTSol,f)

print("cuts : ",m._count)
sys.stdout.close()