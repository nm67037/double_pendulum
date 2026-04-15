import pandas as pd
import matplotlib.pyplot as plt

# Prompt for the file
user_input = input("Enter the CSV filename (press Enter for '20_trq_test.csv'): ").strip()
file_name = user_input if user_input else '20_trq_test.csv'

try:
    # Load the data
    df = pd.read_csv(file_name)

    # 1. Identify the start of the torque step
    # We look for the first moment torque jumps above 2%
    step_mask = df['Torque Feedback (%)'] > 2
    if not step_mask.any():
        print("❌ Error: Could not detect a torque step in the data.")
        exit()
    
    start_idx = df[step_mask].index[0]
    t_start = df.loc[start_idx, 'Time (s)']
    
    # Calculate the average torque applied during the push
    torque_step_value = df.loc[start_idx:, 'Torque Feedback (%)'].mean() 

    # 2. Calculate Steady State (Max) Velocity
    # We only look at velocity data *after* the torque step begins
    df_step = df.loc[start_idx:]
    v_ss = df_step['Velocity Feedback (rpm, mm/s)'].max()

    # 3. Calculate 63.2% threshold and Time Constant (Tau)
    v_target = v_ss * 0.632
    
    # Find the first timestamp where velocity crosses the 63.2% mark
    cross_mask = (df['Time (s)'] >= t_start) & (df['Velocity Feedback (rpm, mm/s)'] >= v_target)
    if not cross_mask.any():
        print("❌ Error: Velocity never reached 63.2% of max.")
        exit()
        
    cross_idx = df[cross_mask].index[0]
    t_cross = df.loc[cross_idx, 'Time (s)']
    
    # The actual Time Constant!
    tau = t_cross - t_start

    # --- Plotting ---
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    # Primary Axis: Velocity
    color1 = 'tab:blue'
    ax1.set_xlabel('Time (s)', fontweight='bold')
    ax1.set_ylabel('Velocity Feedback (mm/s)', color=color1, fontweight='bold')
    ax1.plot(df['Time (s)'], df['Velocity Feedback (rpm, mm/s)'], color=color1, linewidth=2, label='Velocity Curve')
    
    # Annotations for System ID
    ax1.axhline(v_ss, color='green', linestyle='--', alpha=0.7, label=f'Steady State ({v_ss:.1f} mm/s)')
    ax1.axhline(v_target, color='orange', linestyle=':', alpha=0.9, label=f'63.2% Mark ({v_target:.1f} mm/s)')
    
    # Mark the start and cross times
    ax1.axvline(t_start, color='gray', linestyle='-.', alpha=0.5, label='Step Start')
    ax1.plot(t_cross, v_target, 'ro', markersize=8, label=f'Tau Point (\u03C4 = {tau:.3f}s)')

    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax1.legend(loc='upper left')

    # Secondary Axis: Torque
    ax2 = ax1.twinx()  
    color2 = 'tab:red'
    ax2.set_ylabel('Torque Feedback (%)', color=color2, fontweight='bold')
    ax2.plot(df['Time (s)'], df['Torque Feedback (%)'], color=color2, linewidth=1.5, linestyle='-', alpha=0.3, label='Torque Step')
    ax2.tick_params(axis='y', labelcolor=color2)
    ax2.legend(loc='lower right')

    # Formatting and saving
    plt.title('Cart Step Response & System Identification', fontsize=14, fontweight='bold')
    fig.tight_layout() 
    
    save_name = file_name.replace('.csv', '_analysis.png')
    plt.savefig(save_name, dpi=300)
    
    # Show the interactive plot window
    plt.show()

    # --- Console Output ---
    print("\n" + "="*45)
    print("  SYSTEM IDENTIFICATION PARAMETERS")
    print("="*45)
    print(f"Torque Step Applied : ~{torque_step_value:.1f} %")
    print(f"Step Start Time     : {t_start:.3f} s")
    print(f"Steady-State Vel    : {v_ss:.1f} mm/s")
    print(f"63.2% Target Mark   : {v_target:.1f} mm/s")
    print(f"Time at 63.2% Mark  : {t_cross:.3f} s")
    print("-" * 45)
    print(f"Time Constant (\u03C4)   : {tau:.3f} seconds")
    print("="*45)
    print("\nTo calculate Mass (M) and Friction (b) in MATLAB:")
    print("1. Convert Torque (%) to Linear Force (N) -> F_in")
    print("2. b = F_in / Steady-State Vel")
    print("3. M = b * \u03C4\n")

except FileNotFoundError:
    print(f"\n❌ Error: Could not find '{file_name}'.")
except Exception as e:
    print(f"\n❌ Error processing data: {e}")
