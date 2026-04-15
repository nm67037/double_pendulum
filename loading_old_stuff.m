% Load the .mat file into a struct
data = load('/home/vizhins/Documents/UGA_classes/26_SPRING/controls/Compiled Information of Inverted Pendulum/Compiled Information/Inverted Pendulum/100P_test.mat'); 

% See what variables are inside
disp(data);

% Access the 'loading_old_stuff' struct inside 'data'
loading_old_stuff_yo = data.loading_old_stuff_yo;

% Now you can access 'log'
log_data = loading_old_stuff_yo.log;

% Display the first 10 columns of all 6 rows
log_data(:,1:10)