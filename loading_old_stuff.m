% Load the .mat file into a struct
data = load('/home/vizhins/Documents/UGA_classes/26_SPRING/controls/Compiled Information of Inverted Pendulum/Compiled Information/Inverted Pendulum/100P_test.mat'); 

% See exactly what variables are in this .mat file
disp(fieldnames(data))