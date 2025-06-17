import json
import os


# Funktion, die die Daten verarbeitet
def modify_roster(data):
    nurses_position = data["nurses_position"]
    nurse_unav = data["nurse_unav"]
    roster = data["initial_roster"]

    for nurse, days_unav in nurse_unav.items():
        nurse_index = nurses_position[nurse]
        for day in days_unav:
            roster[nurse_index][day] = 0
    
    return roster



if __name__ == "__main__":

    # Pfad zum Verzeichnis mit den JSON-Dateien
    directory_path = 'd14/'


    # Durchlaufe alle Dateien im spezifizierten Verzeichnis
    for filename in os.listdir(directory_path):
        if filename.endswith('.json'):  # Überprüft, ob die Datei eine JSON-Datei ist
            file_path = os.path.join(directory_path, filename)
            
            # Die Datei öffnen und den Inhalt laden
            with open(file_path, 'r') as file:
                data = json.load(file)

            # Modifizierten Roster erhalten und unter dem neuen Schlüssel speichern
            data['disturbed_roster'] = modify_roster(data)

            # Die aktualisierte Datenstruktur zurück in die JSON-Datei schreiben
            with open(file_path, 'w') as file:
                json.dump(data, file, indent=4)

            print(f"Datei {filename} wurde erfolgreich aktualisiert mit dem 'disturbed_roster'.")
