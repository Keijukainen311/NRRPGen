import random
import string
import json


def get_number_of_instances():
    while True:
        try:
            value = int(input("Number of Instances (1-20): "))
            if 1 <= value <= 50:
                return value
            else:
                print("Enter the amount of Instances that should be generated (between 1 and 20).")
        except ValueError:
            print("Not valid. Enter a valid number between 1 and 20.")

def get_number_of_nurses():
    options = ["Small", "Medium", "Large", "Mixed"]
    print("Number of nurses:")
    print("  Small (6-10 nurses)")
    print("  Medium Instances (14-22 nurses)")
    print("  Large Instances (26-30 nurses)")
    print("  Mixed")
    while True:
        choice = input("Choose number of nurses (Small, Medium, Large, Mixed): ").capitalize()
        if choice in options:
            return choice
        else:
            print("Not valid. Enter Small, Medium, Large or Mixed")

def get_complexity_onoff():
    options = ["Little", "Medium", "Hard", "Mixed"]
    while True:
        choice = input("Complexity for On and Off Requests of Nurses (Little, Medium, Hard, Mixed): ").capitalize()
        if choice in options:
            return choice
        else:
            print("Not valid. Enter Little, Medium, Hard or Mixed")

def get_complexity_unav():
    options = ["Little", "Medium", "Hard", "Mixed"]
    while True:
        choice = input("Complexity for unavailability of Nurses (Little, Medium, Hard, Mixed): ").capitalize()
        if choice in options:
            return choice
        else:
            print("Not valid. Enter Little, Medium, Hard or Mixed")

def get_planning_horizon():
    options = ["14", "28"]
    while True:
        choice = input("Planning Horizon (14 days or 28 days): ")
        if choice in options:
            return int(choice)
        else:
            print("Not valid. Enter 14 or 28.")


def get_nurse_count(nurse_category):
    if nurse_category == "Small":
        return random.choice([6, 10])
    elif nurse_category == "Medium":
        return random.randint(14, 22)
    elif nurse_category == "Large":
        return random.choice([26, 30])
    elif nurse_category == "Mixed":
        return get_nurse_count(random.choice(["Small", "Medium", "Large"]))
    else:
        return "Not valid, try again"
    

def get_complexity_value_onoff(complexity):
    if complexity == "Little":
        return (2, 2)
    elif complexity == "Medium":
        on = random.randint(3, 5)
        off = random.randint(3, 5)
        return (on, off)
    elif complexity == "Hard":
        on = random.randint(4, 7)
        off = random.randint(4, 7)
        return (on, off)
    elif complexity == "Mixed":
        return get_complexity_value_onoff(random.choice(["Little", "Medium", "Hard"]))
    else:
        return ("Invalid", "Invalid")


def get_complexity_value_unav(complexity):
    if complexity == "Little":
        nurse = 1
        min = random.randint(1, 2)
        max = random.randint(3, 7)
        return (nurse, min, max)
    elif complexity == "Medium":
        nurse = random.randint(1, 3)
        min = random.randint(1, 2)
        max = random.randint(3, 7)
        return (nurse, min, max)
    elif complexity == "Hard":
        nurse = random.randint(4, 7)
        min = random.randint(1, 3)
        max = random.randint(3, 14)
        return (nurse, min, max)
    elif complexity == "Mixed":
        return get_complexity_value_unav(random.choice(["Little", "Medium", "Hard"]))
    else:
        return ("Invalid", "Invalid", "Invalid")

def generate_nurse_data(n_nurses, n_days=14, n_on_nurses=5, on_min_days=1, on_max_days=3, n_off_nurses=3, off_min_days=2, off_max_days=4):
    # A, B, C...
    def generate_nurse_names(n):
        names = []
        for i in range(n):
            if i < 26:
                names.append(string.ascii_uppercase[i])
            else:
                first_letter = string.ascii_uppercase[(i // 26) - 1]
                second_letter = string.ascii_uppercase[i % 26]
                names.append(first_letter + second_letter)
        return names

    nurse_names = generate_nurse_names(n_nurses)

    # Manuell Mindest & Max Besetzung
    if 6 <= n_nurses <= 10:
        min_nurse = 1
    elif 10 < n_nurses <= 20:
        min_nurse = 2
    elif 20 < n_nurses <= 30:
        min_nurse = 3
    else:
        min_nurse = 4

    if 6 <= n_nurses <= 10:
        max_nurse = 2
    elif 10 < n_nurses <= 20:
        max_nurse = 4
    elif 20 < n_nurses <= 30:
        max_nurse = 6
    else:
        max_nurse = 7

    shifts = ["Day", "Late", "Night"]

    # Generate "on" requests first
    on_nurses = random.sample(nurse_names, min(n_on_nurses, n_nurses))
    day_on_requests = {}
    for nurse in on_nurses:
        on_request_days = random.sample(range(n_days), random.randint(on_min_days, min(on_max_days, n_days)))
        day_on_requests[nurse] = [(day, random.choice(shifts)) for day in on_request_days]

    # Generate "off" requests, ensuring no overlap with "on" request days
    off_nurses = random.sample(nurse_names, min(n_off_nurses, n_nurses))
    day_off_requests = {}
    for nurse in off_nurses:
        if nurse in day_on_requests:
            on_days = {day for day, _ in day_on_requests[nurse]}  # Extract "on" request days for this nurse
            possible_off_days = [day for day in range(n_days) if day not in on_days]  # Exclude "on" days from potential "off" days
        else:
            possible_off_days = list(range(n_days))  # If no "on" requests, all days are available for "off" requests
        day_off_requests[nurse] = random.sample(possible_off_days, random.randint(off_min_days, min(off_max_days, len(possible_off_days))))

    # Nurse positions
    nurses_position = {nurse: i for i, nurse in enumerate(nurse_names)}

    # Define schedule parameters
    schedule_params = {
        "n_nurses": n_nurses,
        "n_days": n_days,
        "max_work_total": 11,
        "min_work_total": 6,
        "hours_per_day": 8,
        "max_consec_days": 6,
        "min_consec_days": 2,
        "max_work_weekend": 2,
        "all_days": [1, 2, 3],
        "forbidden_pattern": [[3, 1], [3, 2]],
        "min_nurse": min_nurse,
        "min_coverage": min_nurse,
        "min_consec_days_off": 2,
        "max_coverage": max_nurse,
        #"pen_min_coverage": 1000, # ist jetzt HC...
        "pen_max_coverage": 1,
        "pen_consecutive_shifts": 3,
        "pen_on_request": 1,
        "pen_off_request": 2,
        "pen_min_consec_off": 3,
        "pen_change_shift": 5,
        "day_off_requests": day_off_requests,
        "nurses_position": nurses_position,
        "day_on_requests": day_on_requests
    }

    return schedule_params

