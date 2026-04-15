import csv
import os

# Get the input file name from the user
user_input = input("Enter the name of the .lsm file to convert (e.g., test_1): ").strip()

# Auto-append .lsm if the user didn't type it
if not user_input.lower().endswith('.lsm'):
    input_file_path = user_input + '.lsm'
else:
    input_file_path = user_input

# Automatically name the output file
output_file_path = input_file_path[:-4] + '.csv'

try:
    # Read the data from the file
    with open(input_file_path, 'r') as file:
        lines = file.readlines()

    # Prepare the CSV file for writing
    with open(output_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        
        # Headers for 2-channel data
        writer.writerow(["Time (s)", "Velocity Feedback (rpm, mm/s)", "Torque Feedback (%)"])

        for line in lines:
            # Skip empty lines and the 'CH1 : Velocity...' header string
            if line.strip() and not line.startswith('CH1'):
                parts = line.split(";")
                
                # Ensure we have at least our two data chunks
                if len(parts) >= 2:
                    time_velocity = parts[0].strip().split()
                    torque = parts[1].strip().split()

                    if len(time_velocity) >= 2 and len(torque) >= 2:
                        time = time_velocity[0]
                        velocity = time_velocity[1]
                        torque_value = torque[1]
                        
                        writer.writerow([time, velocity, torque_value])

    print(f"\n✅ Success! Converted '{input_file_path}' to '{output_file_path}'")

except FileNotFoundError:
    print(f"\n❌ Error: Could not find '{input_file_path}'. Make sure it is in the same folder as this script.")
