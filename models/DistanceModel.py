import sys
import gurobipy as gp
from gurobipy import GRB
import pickle as pk

boundRate = 0.25
districtNum = 8

def EuclieanDistance(A,B):
    return ((A[0]-B[0])**2 + (A[1]-B[1])**2)**(1/2)


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
sys.stdout = open("{}_{}.log".format("DIST",file_name), 'w')

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

# construct adjacency dictionary

adjDist = {}
for v in vertex:
    adjDist[v] = []

for a in arcs:
    adjDist[a[0]].append(a[1])
print(adjDist)

closer = {}  # dictionary where first dimension is the choice of center


for d in vertex:
    for a in adjDist.keys():
        closer[d,a] = []
        distA = EuclieanDistance(pos[a],pos[d])
        for b in adjDist[a]:
            distB = EuclieanDistance(pos[b],pos[d])
            if distB < distA+0.00001:
                closer[d,a].append(b)
    

m = gp.Model('DIST')

#### Hess model ####

# declare assignment binary variable
x = m.addVars(vertex,vertex, vtype=GRB.BINARY ,name="x")

# objective funciton
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


# distance model

m.addConstrs(
    (x[i,j] <= gp.quicksum( x[k,j] for k in closer[j,i]) for i in vertex for j in vertex if i != j )
        , "distance")


m.Params.timelimit = 1800.0
m.optimize()



DISTSol = {}
for i in vertex:
    for j in vertex:
        if x[i,j].x >0.5:
            DISTSol[i] = j

with open("{}_{}.pk".format("DIST",file_name),"wb") as f:
    pk.dump(DISTSol,f)

sys.stdout.close()