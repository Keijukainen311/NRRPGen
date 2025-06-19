import random


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

def get_complexity():
    options = ["Little", "Medium", "Hard", "Mixed"]
    while True:
        choice = input("Complexity (Little, Medium, Hard, Mixed): ").capitalize()
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
    

def get_complexity_value(complexity):
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
        return get_complexity_value(random.choice(["Little", "Medium", "Hard"]))
    else:
        return ("Invalid", "Invalid")

    

def main():
    print("NRRP-Generator. Choose settings:")
    config = {
        "Number of Instances": 5, #get_number_of_instances(),
        "Number of Nurses": "Mixed", #get_number_of_nurses(),
        "Complexity": "Mixed", #get_complexity(),
        "Planning Horizon": "14" #get_planning_horizon()
    }

    print("\nSummary:")
    for key, value in config.items():
        print(f"{key}: {value}")


    # Erstelle die Instanzen basierend auf der Anzahl
    instances = []
    for i in range(1, config["Number of Instances"] + 1):
        on, off = get_complexity_value(config["Complexity"])
        n_nurses = get_nurse_count(config["Number of Nurses"])
        instance = {
            "Instance": f"Instance {i}",
            "Number": n_nurses,
            "Number of Nurses": config["Number of Nurses"],
            "On": on,
            "Off": off,
            "Complexity": config["Complexity"],
            "Planning Horizon": config["Planning Horizon"]
        }
        instances.append(instance)

    print("\nZusammenfassung der Instanzen:")
    for inst in instances:
        print(inst)


        
if __name__ == "__main__":
    main()
