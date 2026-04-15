import csv

# File paths (Make sure these match exactly)
input_file_path = '20_trq_test.lsm'
output_file_path = '20_trq_test.csv'

with open(input_file_path, 'r') as file:
    lines = file.readlines()

with open(output_file_path, 'w', newline='') as file:
    writer = csv.writer(file)
    
    # Updated headers for 2 channels
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

print(f"Success! Converted {input_file_path} to {output_file_path}")
