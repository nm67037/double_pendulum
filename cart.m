s= tf('s');

M = 1; %example in kg
b = 0.5; %example friction

%input is motor torque, output is cart position/motor position

cart_sys = (1/M) / (s*(s+b/M));
vel_sys = s*cart_sys;

%step(_sys)