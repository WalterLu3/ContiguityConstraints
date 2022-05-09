# CS728_project

The usage of all .py files are the same. It takes 5 arguments:

1. adjacency pickle file
2. population pickle file
3. position pickle file
4. population bound
5. district number


For example,

```
python3 CUT.py adj_5_8.pk population_5_8.pk position_5_8.pk 0.02 6
```

runs an experiment with 5 x 8 rectangles, with population bound  (L,U) = ((1-0.02)p, (1+0.02)p), where p is the average population, and number of district number being 6.

The data used for the experiments and case study are in data/ folder.

The results of experiments are stored in experiment_result/ folder. I have output the gurobi solving messages for all experiments into separate .log file.(The .pk files are the solutions stored in python pickle.)


For example, the following file

```
Hess_adj_6_9.pk_bound3_districtNum4.log 
```

stores solution messages for experiment with 6 x 9 rectangles, with population bound  (L,U) = ((1-0.03)p, (1+0.03)p), where p is the average population, and number of district number being 4.
