import sys
import gurobipy as gp
from gurobipy import GRB
import pickle as pk

boundRate = 0.02
districtNum = 6

def EuclieanDistance(A,B):
    return ((A[0]-B[0])**2 + (A[1]-B[1])**2)**(1/2)

#print(len(sys.argv))
if len(sys.argv) < 4:
    print('Usage: hw3-steiner.py adjFile populationFile positionFile')
    quit()

with open(sys.argv[1],"rb") as f:
    adj = pk.load(f)
with open(sys.argv[2],"rb") as f:
    pop = pk.load(f)
with open(sys.argv[3],"rb") as f:
    pos = pk.load(f)

# declare vertices
vertex = list(pop.keys()) 
vertexNum = len(vertex)
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
#for v in vertex:
#    arcs.append((v,v))

m = gp.Model('SHIR')

#### Hess model ####

# declare assignment binary variable
x = m.addVars(vertex,vertex, vtype=GRB.BINARY ,name="x")

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


#### MCF MODEL Starts ####
#flow variable with dimension (a,b,i,j)
flow =  m.addVars(vertex,vertex,arcs, lb=0.0 ,name="flow")

#
#add MCF constraints
m.addConstrs(
    (gp.quicksum(flow[a,b,b,v] for v in vertex if (b,v) in arcs) -
     gp.quicksum(flow[a,b,v,b] for v in vertex if (v,b) in arcs) == x[a,b]
        for a in vertex for b in vertex if a!= b)
            , "MCF_SourceSupply")

m.addConstrs(
    (gp.quicksum(flow[a,b,i,v]  for v in vertex if ((i,v) in arcs )) -
     gp.quicksum(flow[a,b,v,i]  for v in vertex if ((v,i) in arcs )) == 0
        for i in vertex for a in vertex for b in vertex if (a!= b and (i not in [a,b])))
            , "MCF_zeroBalance")

m.addConstrs(
    ( gp.quicksum(flow[a,b,v,b] for v in vertex if (v,b) in arcs) == 0
        for a in vertex for b in vertex if a!= b)
            , "MCF_SourceInflow")

m.addConstrs(
    ( gp.quicksum(flow[a,b,v,j]  for v in vertex if ((v,j) in arcs)) <= x[j,b]
        for j in vertex for a in vertex for b in vertex if (a!= b and j!=b))
            , "MCF_otherNodeInflow")





m.optimize()
MCFSol = {}
for i in vertex:
    for j in vertex:
        if x[i,j].x >0.5:
            MCFSol[i] = j


with open("MCFSol.pd","wb") as f:
    pk.dump(MCFSol,f)
#test = [(c,d) for c in a for d in a if c!= d]
#print(test)
