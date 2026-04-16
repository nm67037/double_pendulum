% --- Physical Parameters ---
% Update these placeholder values with your physical hardware measurements
m1 = 1.0;    % Mass of the cart (kg)
m2 = 0.1;    % Mass of the pendulum (kg)
L  = 0.5;    % Length to pendulum center of mass (m)
g  = 9.81;   % Acceleration due to gravity (m/s^2)

% --- 1. Continuous-Time State-Space Matrices ---
A = [0, 1, 0, 0;
     0, 0, (m2/m1)*g, 0;
     0, 0, 0, 1;
     0, 0, ((m1+m2)*g)/(m1*L), 0];

B = [0;
     1/m1;
     0;
     1/(m1*L)];

C = [0, 0, 1, 0];

D = 0;

% Construct the continuous state-space model
sys_c = ss(A, B, C, D);
sys_c.StateName = {'Cart Position', 'Cart Velocity', 'Pendulum Angle', 'Pendulum Angular Velocity'};
sys_c.OutputName = {'Pendulum Angle'};
sys_c.InputName = {'Force'};

disp('Continuous-Time System:');
sys_c

% --- 2. Discretization for PLC ---
% PLCs run on discrete scan cycles, so we use a Zero-Order Hold (ZOH)
Ts = 0.01; % Your PLC scan time in seconds (e.g., 10ms)
sys_d = c2d(sys_c, Ts, 'zoh');

disp('Discrete-Time System (for PLC):');
sys_d

% --- 3. LQR Control Design ---
% Q penalizes state errors: [w, w_dot, theta, theta_dot]
% Here we put a heavy penalty (100) on the pendulum angle falling
Q = diag([10, 1, 100, 10]); 

% R penalizes actuator effort (how much force your motor uses)
R = 1;                      

% Calculate the optimal feedback gain matrix K
% We use dlqr() for the discrete model
K_d = dlqr(sys_d.A, sys_d.B, Q, R);

disp('Discrete LQR Feedback Gain Matrix (K):');
disp(K_d);