import os
import subprocess
import sys
file = ["5_8","6_9","7_10", "wisconsin"]
method = ["HESS", "SHIR", "MCF" , "DistanceModel","CUT","CUT_all","CUT_preadd"]
# for m in method:
#     for f in file:
#         for distNum in [4,6,8]:
#             #print(m,f,distNum)

assert(sys.argv[1] in method) # make sure method exist
assert(sys.argv[2] in file)  # make sure example exist

print("running with method {}, on example {}, with population tolerance {}, and with district number {}".format(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4]))


command = "python models/{}.py data/adj_{}.pk data/population_{}.pk data/position_{}.pk {} {}".format(sys.argv[1],sys.argv[2],sys.argv[2],sys.argv[2],sys.argv[3],sys.argv[4])
subprocess.run(command.split(" "))