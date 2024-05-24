# Variations of formulating contiguity constraints

This repo is dedicated to implementing different variations of contiguity constraints in political districting. Alogrithms are implemented in Gurobi.

## What is contained in this repo?

The most important repos are:
    1. data repo : contains data for political districting (3 synthetic instances and 1 Wisconsin instance).
        a. Population data
        b. Adjacency data
        c. Positional data.
    2. models : constains models for implementing contiguity constraints
        a. HESS: maximizing compactness and allowing possible discontiguity
        b. SHIR: For each district, we can formulate a set of Steiner Tree constraints to guarantee contiguity.
        c. MCF: Instead of using |T| − 1 as big-M constraint in the Steiner Tree formulation of SHIR: we use multi-commodity formulation to obtain a tighter formulation.
        d. DistanceModel: Using the distance of adjacent pair of units to formulate contiguity constraint.
        e. CUT: It uses the idea of a-b separator and add cutting planes to guarantee contiguity.
        f. CUT_preadd, CUT_all: Variations of CUT with preadded cutting plane.

There is a running script `run.py`.

The way to run it is 

`python run.py {Method} {example name} {population tolerance} {district number}`

1. Method: one of the method described in the last section (case sensitive)
2. Example name:
    a. 5_8: 5 times 8 retangular
    b. 6_9: 6 times 9 retangular
    c. 7_10: 7 times 10 retangular
    d. wisconsin: wisconsin county data (72 connties)
3. Population tolerace : a double. For example, 0.02 means the population is less than (1+0.02) times average population and more than (1-0.02) times average population
4. district number: integer. number of districts to create.

Output:
1. A `.log` file that gives the running log of gurobi.
2. A `.pk` (pickle file) that contains a dictionary of which unit is assigned to which district (note that some units are chosen as the name of a district)


## Use of this repo.
With the `.pk` file, it is easy for user to visualize the district. For more flexible use, user can do something like 
`cd models`
`python HESS.py {adjfile} {populationfile} {positionfile} {tolerance} {districtNum}`

without needing to only use the example in the `data/` folder. But users need to make sure that the format of data files satisfies the ones in the `data/` folder, which is trivial.