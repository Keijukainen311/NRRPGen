from docplex.mp.model import Model
import pandas as pd
import numpy as np
import json 
#import sys
import os
from pathlib import Path

import Generator.transform_array as transform
import Generator.check_hc_inital as hc

# Read Parameter
def load_config(file_path):
    with open(file_path, 'r') as file:
        config = json.load(file)
    return config

def save_config(file_path, config):
    with open(file_path, 'w') as file:
        json.dump(config, file, indent=4)


def solve_nurse_scheduling(n_nurses, n_days, shifts, on_request, off_request, max_coverage, max_work_total, min_work_total, max_consec_days, min_consec_days_off,max_work_weekend, required_coverage, min_consec_days, over_penalty, on_penalty, off_penalty, nurses_position, output=False):
            
    # Create model
    mdl = Model(name="nurse_scheduling")

    # Decision variables
    # x(idt)
    x = mdl.binary_var_dict(
        [(i, j, d) for i in n_nurses for j in shifts for d in n_days],
        name="x"
    )


    #x'idt
    change_indicator = mdl.binary_var_dict(
        [(i, j, d) for i in n_nurses for j in shifts for d in n_days],
        name="change_indicator"
    )


    isRest = mdl.binary_var_dict(
        [(i, d) for i in n_nurses for d in n_days],
        name="isRest"
    )
    # weekend
    k = mdl.binary_var_dict(
        [(i, w) for i in n_nurses for w in range(max_work_weekend)],
        name="k"
    )

    # Under-Coverage
    y = mdl.integer_var_dict(
        [(d, t) for t in shifts for d in n_days],
        name="y"
    )

    # Binary variable to indicate the end of a work block for each nurse and day
    is_end_of_work_block = mdl.binary_var_dict(
        [(i, d) for i in n_nurses for d in n_days],
        name="isEndOfWorkBlock"
    )

    # Binary variable to indicate the end of a rest block for each nurse and day
    is_end_of_rest_block = mdl.binary_var_dict(
        [(i, d) for i in n_nurses for d in n_days],
        name="isEndOfRestBlock"
    )


    # Over-Coverage
    z = mdl.integer_var_dict(
        [(d, t) for t in shifts for d in n_days],
        name="z"
    )

    # On/Off Req
    v = mdl.continuous_var_dict(
        [(i, t, d) for i in n_nurses for t in shifts for d in n_days],
        name="v"
    )


    # Hard Constraints
    # HC1: Each nurse can work at most one shift per day
    for i in n_nurses:
        for d in n_days:
            # The sum of all shifts assigned plus the rest day variable must equal 1
            mdl.add_constraint(
                mdl.sum(x[i, j, d] for j in shifts) + isRest[i, d] == 1,
                f"one_shift_or_rest_per_day_{i}_{d}"
            )

    # Define forbidden shift pairs, e.g., which shifts can't follow which
    forbidden_shifts = {
        "Night": ["Day", "Late"],
    }

    for i in n_nurses:
        for d in range(1, len(n_days)):
            for t in shifts:
                if t in forbidden_shifts:
                    for t_prime in forbidden_shifts[t]:
                        # Add constraint to forbid consecutive forbidden shifts
                        mdl.add_constraint(
                            x[i, t, d-1] + x[i, t_prime, d] <= 1,
                            f"no_{t}_to_{t_prime}_{i}_{d}"
                        )

    
    # HC3: Maximum number of shifts per nurse in the planning period
    for i in n_nurses:
        mdl.add_constraint(mdl.sum(x[i, j, d] for j in shifts for d in n_days) <= max_work_total, f"max_shifts_{i}")


    #HC4: Max. total minutes
    # not necessary, due to max. number of shifts


    # HC5: Minimum number of shifts per nurse
    for i in n_nurses:
        mdl.add_constraint(mdl.sum(x[i, j, d] for j in shifts for d in n_days) >= min_work_total, f"min_shifts_{i}")


    # HC6: Maximum consecutive shifts per nurse
    for i in n_nurses:
        for d in range(len(n_days) - max_consec_days + 1):  # Adjusted to cover all possible starting days
            # Add constraint to ensure the nurse doesn't work more than the allowed max consecutive shifts
            mdl.add_constraint(
                mdl.sum(x[i, j, d + l] for j in shifts for l in range(max_consec_days)) <= max_consec_days-1,
                f"max_consec_shifts_{i}_{d}"
            )


    #HC 7: Minimum consecutive shifts
    # make it to soft constraint..
    # Constraint: Assign either a shift or rest each day (nurse works one shift or takes a rest)
    for i in n_nurses:
        for d in n_days:
            mdl.add_constraint(
                mdl.sum(x[i, j, d] for j in shifts) + isRest[i, d] == 1,
                f"one_shift_or_rest_per_day_{i}_{d}"
            )


    # Constraint: Enforce the end of a work block condition
    for i in n_nurses:
        for d in range(len(n_days) - 1):
            mdl.add_constraint(
                is_end_of_work_block[i, d] >= isRest[i, d + 1] - isRest[i, d],
                f"end_of_work_block_{i}_{d}"
            )
        # Last day constraint: no work block should end on the last day
        mdl.add_constraint(
            is_end_of_work_block[i, len(n_days) - 1] == 0,
            f"end_of_work_block_last_day_{i}"
        )

    for i in n_nurses:
        for d in range(len(n_days)):
            # Calculate the minimum consecutive shifts to enforce
            min_shifts_to_enforce = min(min_consec_days, d + 1) - 1  # min_consec_days - 1 since the last day is marked by the is_end_of_work_block
            
            # Ensure that the required number of consecutive shifts were worked before the block ends
            mdl.add_constraint(
                is_end_of_work_block[i, d] * min_shifts_to_enforce + \
                mdl.sum(isRest[i, d - l] for l in range(1, min_shifts_to_enforce + 1) if d - l >= 0) <= min_shifts_to_enforce,
                f"min_consec_shifts_{i}_{d}"
            )
    

    # Enforce that there is a rest day following the end of a work block
    for i in n_nurses:
        for d in range(len(n_days) - 1):
            mdl.add_constraint(
                is_end_of_work_block[i, d] <= isRest[i, d+1],
                f"rest_after_work_block_{i}_{d}"
            )
    

    
    # HCX: Min Consec Days Off
    # Constraint: End of rest block
    for i in n_nurses:
        for d in range(len(n_days) - 1):
            # Ensure that if today is a rest day and tomorrow is a workday, it marks the end of a rest block
            mdl.add_constraint(
                is_end_of_rest_block[i, d] >= isRest[i, d] - isRest[i, d+1],
                f"end_of_rest_block_{i}_{d}"
            )

    # Constraint: Enforce minimum consecutive days off before starting a work block (similar to Pyomo)
    for i in n_nurses:
        for d in range(len(n_days)):
            # Determine the number of consecutive days off required
            min_days_off_required = min(min_consec_days_off, d + 1) - 1  # -1 because the last day of the rest block is handled by IsEndOfRestBlock
            
            # Sum the previous rest days before day d to check if the nurse has taken enough consecutive days off
            if min_days_off_required > 0:
                rest_days_sum = mdl.sum(isRest[i, prevd] for prevd in range(d - min_days_off_required, d) if prevd >= 0)
                
                # Ensure that the nurse had the required number of consecutive days off before starting work
                mdl.add_constraint(
                    rest_days_sum >= min_days_off_required * is_end_of_rest_block[i, d],
                    f"min_cons_days_off_{i}_{d}"
                )


    # HC8: Maximum number of weekends during the planing period
    weekends = [(k, k + 1) for k in n_days if k % 7 == 5 and k + 1 < len(n_days)]
    

    for i in n_nurses:
        total_weekend_work = mdl.sum(x[i, j, d] for j in shifts for w in weekends for d in w)
        mdl.add_constraint(total_weekend_work <= max_work_weekend, f"max_weekend_work_{i}")


    #HC10: Under Coverage 
    for j in shifts:
        for d in n_days:
            # Ensure that the coverage meets or exceeds the required coverage
            mdl.add_constraint(mdl.sum(x[i, j, d] for i in n_nurses) >= required_coverage[j],
                            f"no_undercoverage_{j}_{d}")
            
    
                
    # Soft Constraints

    # SC1: Constraints for on requests

    on_violation = mdl.binary_var_dict(
        [(nurses_position[i], d, j) for i in on_request for (d, j) in on_request[i]],
        name="on_violation"
    )

    # SC1: Constraints for on requests
    for i in on_request:
        for (d, j) in on_request[i]:
            nurse_idx = nurses_position[i]  # Map nurse name to its numeric index
            mdl.add_constraint(on_violation[nurse_idx, d, j] >= 1 - x[nurse_idx, j, d],
                            f"on_request_violation_{nurse_idx}_{d}_{j}")


    # SC1: Constraints for off requests
    # First Continuous variable 
    off_violation = mdl.binary_var_dict(
        [(i, d, j) for i in off_request for d in off_request[i] for j in off_request[i][d]],
        name="off_violation"
    )
    # Second Constraint...
    for i in off_request:
        for d in off_request[i]:
            for j in off_request[i][d]:
                mdl.add_constraint(x[i, j, d] == off_violation[i, d, j], 
                                f"off_request_violation_{i}_{d}_{j}")

    # SC2: Over Coverage constraints
    # First Continuous variable 
    over_coverage = mdl.continuous_var_dict([(j, d) for j in shifts for d in n_days], name="over_coverage", lb=0)
    # Second Constraint...
    for j in shifts:
        for d in n_days:
            # get, weil sonst index fehler...
            #max_cov = max_coverage.get((j, d), 2)
            mdl.add_constraint(
                mdl.sum(x[i, j, d] for i in n_nurses) - over_coverage[j, d] <= max_coverage,   #+1, weil wegen größer gleich. 
                f"over_coverage_{j}_{d}"
            )



# Objective function components as separate expressions

    on_penalty_expr = mdl.sum(on_penalty * on_violation[nurses_position[i], d, j] 
                    for i in on_request for (d, j) in on_request[i])
    off_penalty_expr = mdl.sum(off_penalty * off_violation[i, d, j] 
                for i in off_request for d in off_request[i] for j in off_request[i][d])
    over_penalty_expr = mdl.sum(over_penalty * over_coverage[j, d] for j in shifts for d in n_days)
    #min_consec_penalty_expr = mdl.sum(min_consec_penalty * min_cons_days_off_violation[i, d] for i in n_nurses for d in n_days)
    #change_penalty_expr = mdl.sum(change_penalty * change_indicator[i, j, d] for i in n_nurses for j in shifts for d in n_days)

    # Total objective
    mdl.minimize(on_penalty_expr + off_penalty_expr + over_penalty_expr ) #+ min_consec_penalty_expr + change_penalty_expr)


    # Solve the model with the initial solution
    solution = mdl.solve(log_output=True)


    # Create an empty dictionary to store the data for the table
    schedule_data = {f"Day {d + 1}": [""] * len(n_nurses) for d in n_days}

    # Fill the dictionary with the schedule information
    if solution:
        #print("Solution found!")
        for d in n_days:
            for i in n_nurses:
                assigned_shifts = []
                for j in shifts:
                    if x[i, j, d].solution_value > 0.5:
                        assigned_shifts.append(j)
                schedule_data[f"Day {d + 1}"][i] = ", ".join(assigned_shifts)
        print("Objective Value:", solution.objective_value)
        print("On Penalty Contribution:", mdl.solution.get_value(on_penalty_expr))
        print("Off Penalty Contribution:", mdl.solution.get_value(off_penalty_expr))
        print("Over Coverage Penalty Contribution:", mdl.solution.get_value(over_penalty_expr))
        mdl.end()
        return transform.dict_to_array(schedule_data,  len(n_nurses), len(n_days)), solution.objective_value
                #print(f"Objective (Penalty): {solution.objective_value}")
    else:
        mdl.end()
        return print("No solution found with IP..."), 99999999


    
    

if __name__ == "__main__":

    folder_path = Path(__file__).parent.parent / 'Instances'

    # Iterate over all generted instences
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        print("Start: ", file_path)
        # Just files no folders...
        if os.path.isfile(file_path):
            config = load_config(file_path)
            #Read all necessary parameters
            n_nurses = range(config['n_nurses'])
            n_days = range(config['n_days'])

            max_work_total = config['max_work_total']
            min_work_total = config['min_work_total']
            hours_per_day = config['hours_per_day']
            min_minutes_total = min_work_total * hours_per_day
            max_consec_days = config['max_consec_days']
            min_consec_days = config['min_consec_days']
            max_work_weekend = config['max_work_weekend']
            all_days = np.array(config['all_days'])
            forbidden_pattern = np.array(config['forbidden_pattern'])
            min_nurse = config['min_nurse']
            min_coverage = config['min_nurse'] 
            min_consec_days_off =config['min_consec_days_off']
            day_off_requests = {key: set(value) for key, value in config['day_off_requests'].items()}
            day_on_requests = {key: set(tuple(value) for value in values) for key, values in config['day_on_requests'].items()}

            over_penalty = config['pen_max_coverage']  # over-coverage
            on_penalty = config['pen_on_request']  # on-request
            off_penalty = config['pen_off_request']  #off request
            min_consec_penalty = config['pen_min_consec_off']   
            max_coverage= config['max_coverage'] 

            nurses_position = config['nurses_position']
            change_penalty = config['pen_change_shift']

            shifts = ["Day", "Late", "Night"]
            pen_consecutive_shifts = config['pen_consecutive_shifts']

            required_coverage = {
                "Day": min_nurse,   
                "Late": min_nurse,  
                "Night": min_nurse
            }

            weekend_days = [k for k in range(len(n_days)) if k % 7 in [5, 6]]
                
            on_request = day_on_requests
            off_request  = transform.transform_shifts_for_ip(day_off_requests, nurses_position, shifts)

            new_array, cost = solve_nurse_scheduling(n_nurses, n_days, shifts, on_request, off_request, max_coverage, max_work_total, min_work_total, max_consec_days, min_consec_days_off,max_work_weekend, required_coverage, min_consec_days, over_penalty, on_penalty, off_penalty, min_consec_penalty, change_penalty, output=False)
            print(new_array)
            print("Zu Kosten: ", cost)
            print("HC2: ", hc.hc2_forbidden_pattern(new_array, n_days))
            print("HC3: ", hc.hc3_max_shifts(new_array, max_work_total))
            print("HC4: ", hc.hc4_max_total_minutes(new_array))
            #print("HC5: ", hc.hc5_min_total_minutes(new_array, hours_per_day, min_minutes_total))
            print("HC6: ", hc.hc6_max_consec_shifts(new_array, max_consec_days))
            print("HC7: ", hc.hc7_min_consec_days(new_array, min_consec_days))
            print("HC8: ", hc.hc8_max_work_weekends(new_array, max_work_weekend))

            data_list = new_array.tolist()

            config["initial_roster"] = data_list
            save_config(file_path, config)


