# PAStar memory predictor

This repository contains a set of scripts to test and predict the memory usage of the PAStar program.

## Requirements

* Python3
    * Plotly 5.13.1
    * Pandas 5.13.1
    * Kaleido (graph engine) 0.2.1
    * Psutil 5.9.0
    * statsmodels 0.13.5
    * tables
    * pandasql
    * numpy

Make sure that all the packages are compatible, since different versions may cause conflicts

## Usage

Run tests
```
python3 -m unittest -v unit_tests.py -b
```

Run the main program
```
python3 ./execution_supervisor.py
```

Build the graphs (**the root of the project must be the working dir**)
```
python3 ./graphs/graphs.py
```

Configuration: modify the *configuration.py* file

## Structure

* Random sequence generator
* Execution supervisor
* Results exporter
* Machine learning

## PAStar repository

Link: https://github.com/danielsundfeld/astar_msa