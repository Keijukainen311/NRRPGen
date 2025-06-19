# Readme

## Nurse Scheduling Instance Generator

This repository contains code to generate instances for a nurse scheduling problem. Each instance specifies constraints such as the number of nurses, the scheduling period, and requirements for working and rest periods.

The output is a series of JSON files stored in the `Instances/` directory, each representing a different scenario with varying team sizes and scheduling rules.

### Features

- Generates realistic re-scheduling scenarios over a 14- and 28-day planning horizon.
- Configurable parameters like:
  - Number of nurses
  - Number of nurses on/off per day
  - Minimum and maximum consecutive working/off days
- Outputs formatted JSON files for easy integration with optimization models.

### Requirements

- Python 3.7+
- [IBM CPLEX Optimization Studio](https://www.ibm.com/products/ilog-cplex-optimization-studio) **must be installed**, as it is required by `docplex`.
- requirements.txt



