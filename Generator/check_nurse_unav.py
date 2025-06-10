import os
import numpy as np
import json

# Folder path containing JSON files
folder_path = 'd14/test/'

# Iterate over all JSON files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith('.json'):
        file_path = os.path.join(folder_path, filename)

        # Load the JSON data from the current file
        with open(file_path) as file:
            data = json.load(file)

        # Extract the initial roster as a NumPy array
        initial_roster = np.array(data['initial_roster'])

        # Get the nurse positions and unavailable days
        nurse_positions = data['nurses_position']
        nurse_unav = data['nurse_unav']

        # Counters for assigned and unassigned nurses
        assigned_count = 0
        not_assigned_count = 0

        # Print file name for clarity
        #print(f"\nProcessing file: {filename}")
        print(initial_roster)
        # Check if nurses in nurse_unav are assigned to shifts
        for nurse, unavailable_days in nurse_unav.items():
            print(nurse)
            print(unavailable_days)
            print(nurse_positions[nurse] )
            nurse_idx = nurse_positions[nurse]  # Get the nurse's index in the roster
            for day in unavailable_days:
                shift_value = initial_roster[nurse_idx][day]
                if shift_value in [1, 2, 3]:
                    assigned_count += 1
                    #print(f"Nurse {nurse} is assigned to a shift on day {day} (Shift: {shift_value}).")
                elif shift_value in [0]:
                    not_assigned_count += 1
                    #print(f"Nurse {nurse} is not assigned to any shift on day {day}.")

        # Summary of assignments for the current file
        print(f"\nSummary for file {filename}:")
        print(f"Assigned shifts: {assigned_count}")
        print(f"Not assigned shifts: {not_assigned_count}")
