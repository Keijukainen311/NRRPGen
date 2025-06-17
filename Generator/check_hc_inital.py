import json 
import numpy as np
import os
from pathlib import Path


# Parameter lesen
def load_config(file_path):
    with open(file_path, 'r') as file:
        config = json.load(file)
    return config


# Parameter lesen
def load_config(file_path):
    with open(file_path, 'r') as file:
        config = json.load(file)
    return config



def hc1_one_shift(array):
    #Always true, the datamodel dont allow multiple assigened shifts
    return True


def hc2_forbidden_pattern(array, n_days):
    #if after evening morning or late, than repeat for this 
    for work_days in array:
        for index, work_day in enumerate(work_days):
            if work_day == 3 and index != len(n_days) -1:
                if work_days[index+1] in (1,2):
                    #print("HC 2 kaputt")
                    return False
            
    return True

#Übergabeparameter?
def hc3_max_shifts(array, max_work_total):
    for work_days in array:
        counter = 0
        for work_day in work_days:
            if work_day != 0:
                counter += 1
        if counter > max_work_total:
            #print("HC 3 kaputt")
            return False

    return True


def hc4_max_total_minutes(array):
    #Aktuell noch volle Shifts, daher über HC 3 drin oder?
    return True


def hc5_min_total_minutes(array, hours_per_day, min_minutes_total, nurse_unav, nurse_position):
    for position, nurse_schedule in enumerate(array):
        nurse_id = [n_id for n_id, pos in nurse_position.items() if pos == position][0]
        unav_days = nurse_unav.get(nurse_id, set())
        worked_days = sum(1 for day_idx, day in enumerate(nurse_schedule) if day != 0 or day_idx in unav_days)
        total_hours = worked_days * hours_per_day
        
        # Check 
        if total_hours < min_minutes_total:
            return False
    return True



def hc6_max_consec_shifts(array, max_consec_days):
    for work_days in array:
        count = 0
        for num in work_days:
            if num > 0:
                count += 1
            else:
                count = 0
            if count > max_consec_days:
                return False
    return True


def hc7_min_consec_days(array, min_consec_days):
    for work_days in array:
        count = 0
        for i, num in enumerate(work_days):
            if num != 0:  
                count += 1
            else:

                if  count > 0 and count < min_consec_days and i - count > 0:
                    print(work_days)
                    return False
                count = 0
    return True


def hc8_min_consec_days_off(array, min_consec_days_off):
    for work_days in array:
        count = 0
        for i, num in enumerate(work_days):
            if num == 0:  # Day off (represented as 0)
                count += 1
            else:
                # If nurse had consecutive days off but fewer than the required amount, return False
                # Ignore this if the count starts on the first day (i == 0)
                if count > 0 and count < min_consec_days_off and i - count > 0:
                    return False
                count = 0
        # At the end of the loop, check if the last consecutive days off are fewer than required,
        # but ignore if this segment ends on the last day of the schedule.
        if count > 0 and count < min_consec_days_off and i != len(work_days) - 1:
            return False
    return True


def hc8_max_work_weekends(array, max_work_weekend):
    n_nurses = len(array)
    n_days = len(array[0])
    n_weeks = n_days // 7
    
    for nurse_id in range(n_nurses):
        work_weekend = 0
        for week in range(n_weeks):
            saturday_index = week * 7 + 5
            sunday_index = week * 7 + 6
            
            if array[nurse_id][saturday_index] > 0:
                work_weekend += 1
            if array[nurse_id][sunday_index] > 0:
                work_weekend += 1
                
            if work_weekend > max_work_weekend:
                #print("HC 8 kaputt")
                return False
    return True



if __name__ == "__main__":
    #select config an write it into paramter.json
    folder_path = Path(__file__).parent.parent / 'Instances'

    # Iterate over all Files..
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            input_file = file_path

        # Config
        config = load_config(input_file)

        # Parameter zuweisen
        n_nurses = config['n_nurses']
        n_days = config['n_days']
        max_work_total = config['max_work_total']
        min_work_total = config['min_work_total']
        hours_per_day = config['hours_per_day']
        min_minutes_total = min_work_total * hours_per_day
        max_consec_days = config['max_consec_days']
        min_consec_days_off = config['min_consec_days_off']
        min_consec_days = config['min_consec_days']
        max_work_weekend = config['max_work_weekend']
        all_days = np.array(config['all_days'])
        forbidden_pattern = np.array(config['forbidden_pattern'])
        min_nurse = config['min_nurse']
        nurse_unav = {key: set(value) for key, value in config['nurse_unav'].items()}
        nurses_position = config['nurses_position']
        initial_roster = np.array(config['initial_roster'])
        

        result_backup = """[[0 2 2 2 2 0 0 1 1 2 1 0 0 2 1 2 1 0 0 2 2 1 1 1 0 0 3 0]
            [1 3 0 0 1 1 1 2 0 0 1 1 1 0 0 1 1 1 2 0 0 0 3 3 3 3 3 0]
            [1 1 2 0 0 2 2 1 1 3 0 0 1 3 0 0 1 1 3 0 0 1 1 1 1 1 0 0]
            [0 1 1 1 2 2 0 0 1 1 1 0 0 2 3 3 3 3 0 0 2 1 2 0 0 1 2 0]
            [0 0 1 2 2 1 0 0 1 2 2 2 3 0 0 1 1 1 2 0 0 2 2 2 2 0 0 3]
            [3 0 0 2 1 0 0 1 1 1 1 1 0 0 2 2 1 1 1 0 0 1 1 1 1 0 0 2]
            [0 1 1 1 1 3 0 0 1 2 1 1 0 0 2 1 1 1 0 0 2 1 1 0 0 1 1 1]
            [1 2 3 3 3 0 0 0 2 1 3 3 3 0 0 0 1 2 1 1 1 0 0 3 3 0 0 1]
            [2 1 1 1 0 0 2 1 2 1 1 0 0 1 3 3 3 3 0 0 1 3 3 0 0 0 0 2]
            [2 2 2 0 0 3 3 3 3 0 0 2 2 3 0 0 2 3 3 0 0 2 2 2 2 3 0 0]
            [3 3 3 3 3 0 0 0 2 2 2 3 0 0 0 0 2 2 2 3 3 0 0 1 2 2 2 3]
            [1 1 1 1 0 0 0 0 0 1 2 1 2 0 0 2 1 1 1 3 0 0 1 1 2 2 1 0]
            [1 1 2 2 0 0 3 3 0 0 1 1 3 3 0 0 1 2 1 1 0 0 1 3 3 3 0 0]
            [1 1 1 1 0 0 1 2 3 3 3 0 0 1 1 1 1 0 0 2 3 3 0 0 1 1 0 0]]"""


        # Convert the list to a 2D NumPy array with the correct shape
        array = np.array(initial_roster).reshape(n_nurses, n_days)
        print(filename)
        #array = np.array(result_backup).reshape(14, 28)
        print(array)
        print("HC2: ", hc2_forbidden_pattern(array, n_days))
        print("HC3: ", hc3_max_shifts(array, max_work_total))
        print("HC4: ", hc4_max_total_minutes(array))
        print("HC5: ", hc5_min_total_minutes(array, hours_per_day, min_minutes_total))
        print("HC6: ", hc6_max_consec_shifts(array, max_consec_days))
        print("HC7: ", hc7_min_consec_days(array, min_consec_days))
        print("HC8: ", hc8_max_work_weekends(array, max_work_weekend))
        print(nurses_position)

