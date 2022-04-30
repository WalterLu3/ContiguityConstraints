import os

file = ["_5_8","_6_9","_7_10"]
method = ["HESS", "SHIR", "DistanceModel","CUT","CUT_all","CUT_preadd"]
for m in method:
    for f in file:
        for distNum in [4,6,8]:
            #print(m,f,distNum)
            command = "python3 {}.py adj{}.pk population{}.pk position{}.pk 0.02 {}".format(m,f,f,f,distNum)
            print(command)