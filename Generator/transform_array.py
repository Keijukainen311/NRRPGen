import numpy as np
import json 



def array_to_dict(array):
    # Shift Mapping
    shift_mapping = {
        1: "Day",
        2: "Late",
        3: "Night",
        0: None  
    }

    dict = {}

    for nurse_index, shifts in enumerate(array):
        for day_index, shift in enumerate(shifts):
            if shift != 0:  # Nur wenn eine Schicht zugewiesen ist!!
                shift_name = shift_mapping[shift]
                dict[(nurse_index, shift_name, day_index)] = 1
    #print(dict2)
    return dict

def dict_to_array(dict, n_nurses, n_days):

    reconstructed_array = np.zeros((n_nurses, n_days), dtype=int)
    #print(reconstructed_array)
    #  Shift Mapping reverse
    reverse_shift_mapping = {
        "Day": 1,
        "Late": 2,
        "Night": 3,
        "" : 0
    }
    
    for day_index, (day, shifts) in enumerate(dict.items()):
        for nurse_index, shift in enumerate(shifts):
            reconstructed_array[nurse_index, day_index] = reverse_shift_mapping[shift]


    return reconstructed_array


def transform_shifts_for_ip(nurse_unav, nurses_position, shifts):
    unavailable_shifts = {}

    # Iterate through the nurse_unav dictionary
    for nurse, unavailable_days in nurse_unav.items():
        nurse_id = nurses_position[nurse]
        unavailable_shifts[nurse_id] = {}

        for day in unavailable_days:
            unavailable_shifts[nurse_id][day] = shifts
    return unavailable_shifts



if __name__ == "__main__":
    

        
    # Parameter lesen
    def load_config(file_path):
        with open(file_path, 'r') as file:
            config = json.load(file)
        return config

    # Config laden

    config_file_path = 'C:/Users/Standardbenutzer/iCloudDrive/Thesis/Implementation/Instances/parameter.json'
    config = load_config(config_file_path)

    # Parameter zuweisen
    n_nurses = config['n_nurses']
    n_days = config['n_days']
    best_solution = np.array([
        [2, 3, 0, 3, 3, 0, 0, 0, 2, 3, 0, 1, 2, 2],
        [0, 2, 2, 0, 2, 3, 1, 0, 2, 1, 1, 2, 1, 0],
        [1, 2, 3, 3, 3, 0, 2, 3, 1, 1, 2, 2, 3, 3],
        [3, 3, 3, 0, 1, 1, 1, 2, 3, 0, 3, 3, 0, 0],
        [0, 1, 2, 1, 0, 2, 0, 0, 0, 0, 3, 0, 0, 0],
        [0, 0, 1, 2, 2, 0, 0, 1, 1, 2, 0, 3, 3, 3]
    ])
    dict = {}
    dict = array_to_dict(best_solution)
    #print(dict)
    array = dict_to_array(dict)
    #print(array)
    print(array == best_solution)

    
