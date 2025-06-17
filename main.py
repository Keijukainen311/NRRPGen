from Generator.first_roster import generate_nurse_data
from Generator.initial_roster import solve_nurse_scheduling, load_config, save_config
import Generator.transform_array as transform
import Generator.check_hc_inital as hc
from Generator.add_unav import simulate_sick_days_for_file

import json
import os
import numpy as np
from pathlib import Path

######################### ##################################
#########       Inital Roster     ##########################
#############################################################

# Example instance generation
nurse_data = generate_nurse_data(
    n_nurses=6,  
    n_on_nurses=2, on_min_days=1, on_max_days=3,  
    n_off_nurses=2, off_min_days=2, off_max_days=4  
)

# Save to JSON
formatted_json_str = json.dumps(nurse_data, indent=4)
with open('Instances/instance1.json', 'w') as json_file:
    json_file.write(formatted_json_str)



######################### ##################################
#########   IP Solver for Inital Roster   ###################
#############################################################
 

folder_path = Path(__file__).parent / 'Instances'

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
        print("Start IP-Sovler for inital Roster...")
        new_array, cost = solve_nurse_scheduling(n_nurses, n_days, shifts, on_request, off_request, max_coverage, max_work_total, min_work_total, max_consec_days, min_consec_days_off,max_work_weekend, required_coverage, min_consec_days, over_penalty, on_penalty, off_penalty, nurses_position, output=False)
        """print(new_array)
        print("Zu Kosten: ", cost)
        print("HC2: ", hc.hc2_forbidden_pattern(new_array, n_days))
        print("HC3: ", hc.hc3_max_shifts(new_array, max_work_total))
        print("HC4: ", hc.hc4_max_total_minutes(new_array))
        #print("HC5: ", hc.hc5_min_total_minutes(new_array, hours_per_day, min_minutes_total))
        print("HC6: ", hc.hc6_max_consec_shifts(new_array, max_consec_days))
        print("HC7: ", hc.hc7_min_consec_days(new_array, min_consec_days))
        print("HC8: ", hc.hc8_max_work_weekends(new_array, max_work_weekend))"""
        print("Inital Roster added..")
        data_list = new_array.tolist()

        config["initial_roster"] = data_list
        save_config(file_path, config)



######################### ##################################
#########      Add Unav            ##################
#############################################################


## Hier noch eine Loop einbauen? Damit alle Files angepackt werden.
file = Path(__file__).parent / 'Instances/instance1.json'
simulate_sick_days_for_file(
     filename=file, 
      n_unav_nurses=1, unav_min_days=1, unav_max_days=2 , 
     output_filename=file
 )




######################### ##################################
#########      Add Dist Roster            ##################
#############################################################

