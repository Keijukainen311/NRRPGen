import json
import numpy as np
import random

# Function to simulate sick days, considering only assigned days
def simulate_sick_days(nurse_names, initial_roster, n_unav_nurses, unav_min_days, unav_max_days):
    n_nurses, n_days = initial_roster.shape

    # Randomly select nurses who will be unavailable (sick)
    unav_nurses = random.sample(nurse_names, min(n_unav_nurses, n_nurses))
    
    # Simulate unavailable days for these nurses based on when they are assigned (1-3 in the roster)
    nurse_unav = {}
    for nurse in unav_nurses:
        nurse_idx = nurse_names.index(nurse)
        assigned_days = np.where(initial_roster[nurse_idx] > 0)[0]  # Only consider assigned days (1-3)
        
        if len(assigned_days) > 0:
            # Randomly pick unavailable days (sick days) only from assigned days
            unav_days = random.sample(list(assigned_days), random.randint(unav_min_days, min(unav_max_days, len(assigned_days))))
            nurse_unav[nurse] = [int(day) for day in unav_days]  # Convert to native Python int for JSON compatibility

    return nurse_unav

# Function to save the modified data to JSON
def save_to_json(nurse_data, output_path):
    # Save the modified JSON with the sick days
    with open(output_path, 'w') as json_file:
        json.dump(nurse_data, json_file, indent=4)
    print(f"Data has been saved to {output_path}")

# Main function to handle file loading, sick day simulation, and saving
def simulate_sick_days_for_file(filename, n_unav_nurses, unav_min_days, unav_max_days, output_filename):
    # Load the existing JSON file
    with open(filename, 'r') as json_file:
        nurse_data = json.load(json_file)

    # Extract the necessary details from the JSON data
    initial_roster = np.array(nurse_data['initial_roster'])
    nurse_names = sorted(nurse_data['nurses_position'], key=nurse_data['nurses_position'].get)

    # Simulate sick days and add them to the JSON data
    nurse_unav = simulate_sick_days(nurse_names, initial_roster, n_unav_nurses, unav_min_days, unav_max_days)

    # Add the sick day information in a similar format to 'day_off_requests'
    nurse_data['nurse_unav'] = nurse_unav

    # Convert NumPy arrays in the 'initial_roster' to Python lists for JSON serialization
    nurse_data['initial_roster'] = initial_roster.tolist()

    # Save the modified data to a new JSON file
    save_to_json(nurse_data, output_filename)

"""# Instance 1:
simulate_sick_days_for_file(
     filename='d28_w_roster/instance1.json', 
      n_unav_nurses=1, unav_min_days=1, unav_max_days=2 , 
     output_filename='d28_w_roster/instance1.json'
 )
   
# Instance 2:
simulate_sick_days_for_file(
     filename='d28_w_roster/instance2.json', 
      n_unav_nurses=3, unav_min_days=1, unav_max_days=2  ,
     output_filename='d28_w_roster/instance2.json'
 )

# Instance 3
simulate_sick_days_for_file(
     filename='d28_w_roster/instance3.json', 
     n_unav_nurses=1, unav_min_days=1, unav_max_days=2  ,
     output_filename='d28_w_roster/instance3.json'
 )
# Instance 4:
simulate_sick_days_for_file(
     filename='d28_w_roster/instance4.json', 
     n_unav_nurses=3, unav_min_days=1, unav_max_days=2 ,
     output_filename='d28_w_roster/instance4.json'
 )
# Instance 5:
simulate_sick_days_for_file(
     filename='d28_w_roster/instance5.json', 
    n_unav_nurses=1, unav_min_days=1, unav_max_days=2  , 
     output_filename='d28_w_roster/instance5.json'
 )
# Instance 6:
simulate_sick_days_for_file(
     filename='d28_w_roster/instance6.json', 
     n_unav_nurses=3, unav_min_days=1, unav_max_days=2  , 
     output_filename='d28_w_roster/instance6.json'
 )

# Instance 7:
simulate_sick_days_for_file(
     filename='d28_w_roster/instance7.json', 
    n_unav_nurses=3, unav_min_days=1, unav_max_days=2  , 
     output_filename='d28_w_roster/instance7.json'
 )
# Instance 8
simulate_sick_days_for_file(
     filename='d28_w_roster/instance8.json', 
     n_unav_nurses=1, unav_min_days=1, unav_max_days=2 , 
     output_filename='d28_w_roster/instance8.json'
 )
# Instance 9:
simulate_sick_days_for_file(
     filename='d28_w_roster/instance9.json', 
     n_unav_nurses=3, unav_min_days=1, unav_max_days=2 , 
     output_filename='d28_w_roster/instance9.json'
 )
# Instance 10:
simulate_sick_days_for_file(
     filename='d28_w_roster/instance10.json', 
     n_unav_nurses=3, unav_min_days=1, unav_max_days=2  , 
     output_filename='d28_w_roster/instance10.json'
 )
# Instance 11:
simulate_sick_days_for_file(
     filename='d28_w_roster/instance11.json', 
     n_unav_nurses=1, unav_min_days=1, unav_max_days=2 , 
     output_filename='d28_w_roster/instance11.json'
 )
# Instance 12:
simulate_sick_days_for_file(
     filename='d28_w_roster/instance12.json', 
     n_unav_nurses=3, unav_min_days=1, unav_max_days=2 , 
     output_filename='d28_w_roster/instance12.json'
 )
# Instance 13:
simulate_sick_days_for_file(
     filename='d28_w_roster/instance13.json', 
      n_unav_nurses=3, unav_min_days=1, unav_max_days=7 , 
     output_filename='d28_w_roster/instance13.json'
 )
# Instance 14:
simulate_sick_days_for_file(
     filename='d28_w_roster/instance14.json', 
     n_unav_nurses=1, unav_min_days=1, unav_max_days=3, 
     output_filename='d28_w_roster/instance14.json'
 )
# Instance 15:
simulate_sick_days_for_file(
     filename='d28_w_roster/instance15.json', 
     n_unav_nurses=1, unav_min_days=1, unav_max_days=7, 
     output_filename='d28_w_roster/instance15.json'
 )
# Instance 16:
simulate_sick_days_for_file(
     filename='d28_w_roster/instance16.json', 
     n_unav_nurses=5, unav_min_days=1, unav_max_days=7, 
     output_filename='d28_w_roster/instance16.json'
 )
# Instance 17:
simulate_sick_days_for_file(
     filename='d28_w_roster/instance17.json', 
     n_unav_nurses=1, unav_min_days=1, unav_max_days=14 ,
     output_filename='d28_w_roster/instance17.json'
 )"""
# Instance 18:
simulate_sick_days_for_file(
     filename='d14_w_roster/instance18.json', 
     n_unav_nurses=4, unav_min_days=1, unav_max_days=7, 
     output_filename='d14_w_roster/instance18.json'
 )
"""# Instance 19:
simulate_sick_days_for_file(
     filename='d28_w_roster/instance19.json', 
     n_unav_nurses=7, unav_min_days=1, unav_max_days=7, 
     output_filename='d28_w_roster/instance19.json'
 )
"""