import pandas as pd
import matplotlib.pyplot as plt

# Prompt for the file, defaulting to the one you just converted
user_input = input("Enter the CSV filename (press Enter for '20_trq_test.csv'): ").strip()
file_name = user_input if user_input else '20_trq_test.csv'

try:
    # Load the data using pandas
    df = pd.read_csv(file_name)

    # Set up the figure and the primary axis (Velocity)
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    color1 = 'tab:blue'
    ax1.set_xlabel('Time (s)', fontweight='bold')
    ax1.set_ylabel('Velocity Feedback (mm/s)', color=color1, fontweight='bold')
    ax1.plot(df['Time (s)'], df['Velocity Feedback (rpm, mm/s)'], color=color1, linewidth=2, label='Velocity')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.grid(True, linestyle='--', alpha=0.7)

    # Create a secondary axis sharing the same X-axis (Torque)
    ax2 = ax1.twinx()  
    
    color2 = 'tab:red'
    ax2.set_ylabel('Torque Feedback (%)', color=color2, fontweight='bold')
    ax2.plot(df['Time (s)'], df['Torque Feedback (%)'], color=color2, linewidth=2, linestyle='--', label='Torque')
    ax2.tick_params(axis='y', labelcolor=color2)

    # Formatting and display
    plt.title('Cart Step Response: Velocity & Torque vs. Time', fontsize=14, fontweight='bold')
    fig.tight_layout() 
    plt.show()

except FileNotFoundError:
    print(f"\n❌ Error: Could not find '{file_name}'. Make sure it is in the same folder.")
except KeyError as e:
    print(f"\n❌ Error: The CSV doesn't have the expected column headers. {e}")
