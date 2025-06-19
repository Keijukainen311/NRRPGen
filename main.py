import Generator.first_roster as fr
from Generator.initial_roster import solve_nurse_scheduling, load_config, save_config
import Generator.transform_array as transform
import Generator.check_hc_inital as hc
from Generator.add_unav import simulate_sick_days_for_file
from Generator.add_dist_roster import modify_roster
import json
import os
import random
import numpy as np
from pathlib import Path





def main():

######################### ##################################
#########       Set Parameters     ##########################
#############################################################

    print("NRRP-Generator. Choose settings:")
    config_paramter = {
        "Number of Instances": fr.get_number_of_instances(),
        "Number of Nurses": fr.get_number_of_nurses(),
        "Complexity On / Off Request": fr.get_complexity_onoff(),
        "Complexity Nurse unavailable": fr.get_complexity_unav(),
        "Planning Horizon": fr.get_planning_horizon()
    }

    print("\nSummary:")
    for key, value in config_paramter.items():
        print(f"{key}: {value}")


    # Loop over instances
    for i in range(1, config_paramter["Number of Instances"] + 1):
        on, off = fr.get_complexity_value_onoff(config_paramter["Complexity On / Off Request"])
        nurse_unav, min_unavs, max_unavs = fr.get_complexity_value_unav(config_paramter["Complexity Nurse unavailable"])
        n_nurses = fr.get_nurse_count(config_paramter["Number of Nurses"])
        nurse_data = fr.generate_nurse_data(
            n_nurses=n_nurses,  
            n_on_nurses=on, on_min_days=1, on_max_days=3,  
            n_off_nurses=off, off_min_days=2, off_max_days=4  
        )


    ######################### ##################################
    #########       Inital Roster     ##########################
    #############################################################
        file_name = f"instance{i}.json"
        file = Path(__file__).parent / 'Instances' / file_name
        formatted_json_str = json.dumps(nurse_data, indent=4)
        with open(file, 'w') as json_file:
            json_file.write(formatted_json_str)

    ######################### ##################################
    #########   IP Solver for Inital Roster   ###################
    #############################################################
    
        print("Start IP-Solver: ", file_name)

        config = load_config(file)
        #Read all necessary parameters
        n_nurses = range(config['n_nurses'])
        n_days = range(config['n_days'])

        max_work_total = config['max_work_total']
        min_work_total = config['min_work_total']
        hours_per_day = config['hours_per_day']
        max_consec_days = config['max_consec_days']
        min_consec_days = config['min_consec_days']
        max_work_weekend = config['max_work_weekend']
        all_days = np.array(config['all_days'])
        forbidden_pattern = np.array(config['forbidden_pattern'])
        min_nurse = config['min_nurse']
        min_consec_days_off =config['min_consec_days_off']
        day_off_requests = {key: set(value) for key, value in config['day_off_requests'].items()}
        day_on_requests = {key: set(tuple(value) for value in values) for key, values in config['day_on_requests'].items()}
        over_penalty = config['pen_max_coverage']  # over-coverage
        on_penalty = config['pen_on_request']  # on-request
        off_penalty = config['pen_off_request']  #off request
        max_coverage= config['max_coverage'] 
        nurses_position = config['nurses_position']
        shifts = ["Day", "Late", "Night"]
        required_coverage = {
            "Day": min_nurse,   
            "Late": min_nurse,  
            "Night": min_nurse
        }                
        on_request = day_on_requests
        off_request  = transform.transform_shifts_for_ip(day_off_requests, nurses_position, shifts)
        print("Start IP-Sovler for inital Roster...")
        new_array, cost = solve_nurse_scheduling(n_nurses, n_days, shifts, on_request, off_request, max_coverage, max_work_total, min_work_total, max_consec_days, min_consec_days_off,max_work_weekend, required_coverage, min_consec_days, over_penalty, on_penalty, off_penalty, nurses_position, output=False)
        print("Inital Roster added..")
        data_list = new_array.tolist()

        config["initial_roster"] = data_list
        save_config(file, config)



        ######################### ##################################
        #########      Add Unav            ##################
        #############################################################


        
        simulate_sick_days_for_file(
            filename=file, 
            n_unav_nurses=nurse_unav, unav_min_days=min_unavs, unav_max_days=max_unavs,
            output_filename=file
        )

        ######################### ##################################
        #########      Add Dist Roster            ##################
        #############################################################
        
        with open(file, 'r') as f:
            data = json.load(f)
        # Mody inital roster
        data['disturbed_roster'] = modify_roster(data)
        # Write back
        with open(file, 'w') as json_file:
            json.dump(data, json_file, indent=4)




if __name__ == "__main__":
    main()
