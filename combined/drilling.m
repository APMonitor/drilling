clear all; close all; clc

addpath('apm')

% define server and application
s = 'http://byu.apmonitor.com';
a = 'drill';

% Clear prior application
apm(s,a,'clear all');

% Load model file
apm_load(s,a,'drilling.apm');

% Global settings
apm_option(s,a,'apm.solver',1);
apm_option(s,a,'apm.max_iter',200);

apm_option(s,a,'apm.diaglevel',0);

% Adjustable parameters
apm_info(s,a,'FV','Ro_a_1');
apm_info(s,a,'FV','f_a_2');
apm_info(s,a,'FV','Ro_a_2');
apm_info(s,a,'FV','f_a_3');
apm_info(s,a,'FV','Ro_a_3');
apm_info(s,a,'FV','f_a_4');
apm_info(s,a,'FV','Ro_a_4');
apm_info(s,a,'FV','f_a_5');
apm_info(s,a,'FV','Ro_a_5');
apm_info(s,a,'FV','f_a_6');
apm_info(s,a,'FV','Ro_a_6');
apm_info(s,a,'FV','f_a_7');
apm_info(s,a,'FV','Ro_a_7');
apm_info(s,a,'FV','f_a_8');
apm_info(s,a,'FV','Ro_a_8');
apm_info(s,a,'FV','f_a_9');
apm_info(s,a,'FV','Ro_a_9');
apm_info(s,a,'FV','f_a_10');
apm_info(s,a,'FV','Ro_a_10');
apm_info(s,a,'FV','n');


% Define MVs
apm_info(s,a,'MV','z_choke');
apm_info(s,a,'MV','q_p');
apm_info(s,a,'MV','wob_sp');
apm_info(s,a,'MV','rpm');

% Define CVs
apm_info(s,a,'CV','p_c');
apm_info(s,a,'CV','p_a_1');
apm_info(s,a,'CV','rop');
apm_info(s,a,'CV','q_x');

% Start with a steady state solution
apm_option(s,a,'apm.imode',1);
output = apm(s,a,'solve');
disp('Steady State Solution --------------');
disp(output);

% Load data file
csv_load(s,a,'drilling.csv');
apm_option(s,a,'apm.csv_read',1);

disp('Dynamic Optimization Initialization --------------');
% Solve dynamic optimization problem
apm_option(s,a,'apm.imode',7);
apm_option(s,a,'apm.nodes',2);
apm_option(s,a,'apm.coldstart',0);
%apm_option(s,a,'apm.time_shift',0)
output = apm(s,a,'solve');
apm_get(s,a,'results.csv');
disp(output);


% Manipulated variable tuning

% MV: q_p
apm_option(s,a,'q_p.status',1);
apm_option(s,a,'q_p.fstatus',0);
apm_option(s,a,'q_p.dmax',0.1);  % rate of change limits
apm_option(s,a,'q_p.dcost',80000); % adding cost for change
apm_option(s,a,'q_p.lower',0.01);  % lower limit
apm_option(s,a,'q_p.upper',1.5);  % upper limit
%apm_option(s,a,'q_p.cost',1000)
   
% MV: z_choke
apm_option(s,a,'Z_choke.status',1);
apm_option(s,a,'Z_choke.fstatus',0);
apm_option(s,a,'Z_choke.dmax',0.1);  % rate of change limits
%apm_option(s,a,'Z_choke.dcost',0) % adding cost for change
apm_option(s,a,'Z_choke.dcost',5); % adding cost for change
apm_option(s,a,'Z_choke.lower',0);  % lower limit
apm_option(s,a,'Z_choke.upper',1);  % upper limit
%apm_option(s,a,'Z_choke.cost',0)

% MV: rpm 
apm_option(s,a,'RPM.status',1);
apm_option(s,a,'RPM.fstatus',0);
apm_option(s,a,'RPM.dmax',10);  % rate of change limits
%apm_option(s,a,'Z_choke.dcost',0) % adding cost for change
apm_option(s,a,'RPM.dcost',0.6); % adding cost for change
apm_option(s,a,'RPM.lower',50);  % lower limit
apm_option(s,a,'RPM.upper',500);  % upper limit
%apm_option(s,a,'RPM.cost',0.02)

% Define target values for CVs
apm_option(s,a,'p_c.sphi',35.0);
apm_option(s,a,'p_c.splo',30.0);
apm_option(s,a,'p_c.wsphi',10.0);
apm_option(s,a,'p_c.wsplo',10.0);
apm_option(s,a,'p_c.status',0);

apm_option(s,a,'p_a_1.sphi',315.0);
apm_option(s,a,'p_a_1.splo',300.0);
apm_option(s,a,'p_a_1.wsphi',10.0);
apm_option(s,a,'p_a_1.wsplo',10.0);
apm_option(s,a,'p_a_1.status',0);

apm_option(s,a,'q_x.sphi',0);
apm_option(s,a,'q_x.splo',0);
apm_option(s,a,'q_x.wsphi',10000.0);
apm_option(s,a,'q_x.wsplo',10000.0);
apm_option(s,a,'q_x.status',1);

apm_option(s,a,'rop.sphi',50);
apm_option(s,a,'rop.splo',0);
apm_option(s,a,'rop.wsphi',10000.0);
apm_option(s,a,'rop.wsplo',10000.0);
apm_option(s,a,'rop.status',1);
apm_option(s,a,'rop.cost',-10.0);
apm_option(s,a,'rop.tr_init',0);

disp('Dynamic Optimization --------------');
% Load in new CSV file
apm(s,a,'clear csv');
csv_load(s,a,'results.csv');
%csv_load(s,a,'q_x.csv');
apm_option(s,a,'apm.reqctrlmode',3);
apm_option(s,a,'apm.timeshift',0);
apm_option(s,a,'apm.imode',6);
apm_option(s,a,'apm.coldstart',0);
output = apm(s,a,'solve');
disp(output);

z = apm_sol(s,a);
y = z.x;

figure(1)
subplot(2,1,1)
plot(y.time,y.p_c,'r-')
hold on
plot(y.time,y.p_a_1,'b--')
legend('Choke Pressure','Bit Pressure')
ylabel('Pressure (bar)')

subplot(2,1,2)
plot(y.time,y.q_x,'r-')
hold on
xlabel('Time (sec)')
ylabel('q_x (m^3/s)')

figure(2)
subplot(2,2,1)
plot(y.time,y.q_p,'r-')

ylabel('q_p (m^3/s)')

subplot(2,2,2)
plot(y.time,y.z_choke,'r-')

ylabel('z_choke (%)')

subplot(2,2,3)
plot(y.time,y.rpm,'r-')
hold on
plot(y.time,y.drpm,'b-')
ylabel('rpm ')

subplot(2,2,4)
plot(y.time,y.wob,'r-')
hold on
plot(y.time,y.wob_sp,'b-')
ylabel('wob ')


