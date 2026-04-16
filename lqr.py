import time
import math
from pymodbus.client import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.exceptions import ModbusException

class LQRController:
    def __init__(self, K):
        # K Matrix from MATLAB: [x, theta, x_dot, theta_dot]
        self.K = K
        self.prev_theta_rad = 0.0
        self.last_time = time.time()
        
        # OUTPUT LIMITS (Torque command limits for %MW200)
        self.maxout = 30
        self.minout = -30
        
    def compute(self, x_m, theta_rad, x_dot_ms):
        current_time = time.time()
        dt = current_time - self.last_time
        
        # Prevent divide-by-zero on first loop
        if dt <= 0:
            dt = 1e-16
            
        # 1. Calculate theta_dot (rad/s) numerically since the PLC doesn't provide it
        theta_dot_rads = (theta_rad - self.prev_theta_rad) / dt
        
        # 2. Compute the Full State Feedback Control Law: u = -Kx
        force_newtons = -(
            self.K[0] * x_m + 
            self.K[1] * theta_rad + 
            self.K[2] * x_dot_ms + 
            self.K[3] * theta_dot_rads
        )
        
        # 3. Convert physical force (Newtons) to your Servo Torque Command.
        # This acts as a tuning scalar mapping ideal physics to your actual motor.
        FORCE_TO_TORQUE_SCALAR = 1.0 # TUNE THIS: Start small and increase if response is sluggish
        torque_command = force_newtons * FORCE_TO_TORQUE_SCALAR
        
        # Output clamping
        if torque_command > self.maxout:
            torque_command = self.maxout
        elif torque_command < self.minout:
            torque_command = self.minout
            
        self.prev_theta_rad = theta_rad
        self.last_time = current_time
        
        return torque_command

# ==========================================
# Configuration
# ==========================================
PLC_IP = '192.168.1.2'
PLC_PORT = 502
SLAVE_ID = 1

READ_ADDRESS = 100 # Adjusted to standard LS mapping for %MW100
READ_COUNT = 8    
WRITE_ADDRESS = 200 # Adjusted to standard LS mapping for %MW200
UPDATE_INTERVAL = 0.008 

# --- LQR Parameters & Conversions ---
CART_CENTER = 1633      
BASE_ANGLE = 2046       

# Physical Conversions (Crucial for the MATLAB K-Matrix to work)
M_PER_PULSE = 0.00003414                 # Derived from your ST notes (0.003414 cm)
RAD_PER_PULSE = (2 * math.pi) / 4096     # Assuming a standard 12-bit (4096) encoder

def main():
    client = ModbusTcpClient(PLC_IP, port=PLC_PORT)

    print(f"Connecting to LS PLC at {PLC_IP}...")
    if not client.connect():
        print("Connection failed.")
        return

    print("Connected successfully! Starting LQR loop...\n")

    # The K matrix you generated in MATLAB
    K_lqr = [-100.0000, 393.4081, -89.3339, 41.5658]
    lqr_controller = LQRController(K=K_lqr)
    
    try:
        while True:
            # 1. READ FROM PLC
            try:
                read_result = client.read_input_registers(address=READ_ADDRESS, count=READ_COUNT, slave=SLAVE_ID)
                if read_result.isError():
                    continue
                    
                decoder = BinaryPayloadDecoder.fromRegisters(read_result.registers, byteorder=Endian.Big, wordorder=Endian.Little)
                torque = decoder.decode_16bit_int()
                decoder.skip_bytes(2) 
                position = decoder.decode_32bit_int()
                speed = decoder.decode_32bit_int()
                encoder = decoder.decode_32bit_int()

            except ModbusException:
                continue
            
            # 2. CONVERT TO PHYSICAL SI UNITS
            # x: Cart position error in meters
            x_m = (position - CART_CENTER) * M_PER_PULSE
            
            # theta: Pendulum angle error in radians
            theta_rad = (encoder - BASE_ANGLE) * RAD_PER_PULSE
            
            # x_dot: Cart velocity in meters/second
            # (Assuming the PLC 'speed' variable is in pulses/sec. If it is in RPM or mm/s, adjust this!)
            x_dot_ms = speed * M_PER_PULSE 
            
            # 3. LQR EXECUTION
            # Keep the safety deadband so it doesn't violently actuate if the pendulum is resting down
            if (1600 < encoder < 2500):
                write_counter = lqr_controller.compute(x_m, theta_rad, x_dot_ms)
            else:
                write_counter = 0
                # Reset the differentiator time so it doesn't spike when picked back up
                lqr_controller.last_time = time.time() 

            # 4. WRITE TO PLC
            try:
                modbus_value = int(write_counter) & 0xFFFF
                client.write_register(address=WRITE_ADDRESS, value=modbus_value, slave=SLAVE_ID)
                
                print(f"Pos(m): {x_m:.3f} | Ang(rad): {theta_rad:.3f} | Out: {int(write_counter)}")
            
            except ModbusException:
                pass

            time.sleep(UPDATE_INTERVAL)

    except KeyboardInterrupt:
        print("\nScript stopped by user.")
    finally:
        client.close()

if __name__ == "__main__":
    main()
