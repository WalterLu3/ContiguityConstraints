import sys
import gurobipy as gp
from gurobipy import GRB
import pickle as pk


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
sys.stdout = open("{}_{}.log".format("SHIR",file_name), 'w')


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

#m.optimize()

# m.write("Hess.sol")

# hessSol = {}
# for i in vertex:
#     for j in vertex:
#         if x[i,j].x >0.5:
#             hessSol[i] = j

#### SHIR MODEL Starts ####
flow =  m.addVars(vertex,arcs, lb=0.0 ,name="flow")

#add SHIR constraints
m.addConstrs(
    (gp.quicksum(flow[j,i,v] for v in vertex if (i,v) in arcs) -
     gp.quicksum(flow[j,v,i] for v in vertex if (v,i) in arcs)  == -x[i,j] 
            for i in vertex for j in vertex if i != j)
            , "SHIRnotCenter")

m.addConstrs(
    ( gp.quicksum(flow[j,v,i] for v in vertex if (v,i) in arcs) <= (vertexNum-1) * x[i,j]
        for i in vertex for j in vertex if i != j ), "flowConstr")

m.addConstrs(
    ( gp.quicksum(flow[j,v,j] for v in vertex if (v,j) in arcs) == 0 for j in vertex), "SHIRCenter")

#a = [1,2,3]
m.Params.timelimit = 1800.0
m.optimize()
m.write("SHIR.sol")
SHIRSol = {}
for i in vertex:
    for j in vertex:
        if x[i,j].x >0.5:
            SHIRSol[i] = j


with open("{}_{}.pk".format("SHIR",file_name),"wb") as f:
    pk.dump(SHIRSol,f)
#test = [(c,d) for c in a for d in a if c!= d]
#print(test)
sys.stdout.close()