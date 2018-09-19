import numpy as np
from gekko import GEKKO
import matplotlib.pyplot as plt

# Dynamic hydraulic model for pressure predictions with MPD
m = GEKKO()

# Constants
p_0 = m.Const(1)               # pressure downstream of the choke valve [bar]    
g   = m.Const(9.81)            # gravitational constant
M_d = m.Const(2500)            # Lumped Density per length of Mud in Drill String [kg/m^4 * 1e5]
M_a = m.Const(800)             # Lumped Density per length of Mud in Annulus [kg/m^4 * 1e5]
Ad  = m.Const(0.01025562)      # Cross-sectional Area of Drill String [m^2]
Aa  = m.Const(0.1)             # Cross-sectional Area of Annulus [m^2]

# Parameters
Kc     = m.Param(0.3639)       # Valve Coefficient 
Beta_d = m.Param(90000)        # Bulk Modulus of Mud in Drill String [bar]
Beta_a = m.Param(50000)    
f_d    = m.Param(80)           # Friction Factor in the drill string [bar*s^2/m^6]
f_a    = m.Param(330)          # Friction Factor in the Annulus [bar*s^2/m^6]
Ro_d   = m.Param(1240)         # Mud Density in the Drill String [kg/m^3]        
Ro_a   = m.FV(1290,lb=Ro_d)    # Mud Density in the Drill String Annulus [kg/m^3]    
q_p = m.Param(2.0)             # Flow Rate through Pump [m^3/min] 
z_choke = m.Param(30)          # Choke Valve Opening from 0-100 [%]
q_res = m.Param(0)             # reservoir gas influx flow rate [m^3/min]
q_back = m.Param(0)            # back pressure pump flow rate [m^3/min]
ROP = m.Param(0)               # rate of penetration (m/min)

# Variables
q_bit = m.Var(0.1,lb=0)        # Flow Rate through Bit [m^3/min] 
q_choke = m.Var(1,lb=0)        # Flow Rate through Choke [m^3/min]
p_p = m.Var(50)                # Pressure at Pump [bar]
p_c = m.Var(5,lb=p_0)          # Pressure at Choke Valve [bar]
p_bit = m.Var(450)             # Bit pressure [bar]
h_bit = m.Var(3596)          # Total vertical depth of well [m]

# Intermediates
M = m.Intermediate(M_d+M_a)    # Total Mud Density per length [kg/m^4]
Va = m.Intermediate(Aa*h_bit)  # Volume of Annulus [m^3]
Vd = m.Intermediate(Ad*h_bit)  # Volume of Drill String [m^3]
# Bit pressure [bar]
p_bit0 = m.Intermediate(p_c + (Ro_a*(f_a/3600)*h_bit*(q_bit**2) + Ro_a*g*h_bit)*1e-5) 
# Flow Rate through Choke Valve [m^3/min] 
q_choke0 = m.Intermediate(Kc * z_choke * m.sqrt(Ro_a*(p_c-p_0)*1e-5))

# Equations
m.Equation(p_bit == p_bit0)
m.Equation(q_choke == q_choke0)
m.Equation(Va*p_c.dt()/Beta_a == q_bit + q_back - q_choke + q_res - ROP * Aa)
m.Equation(M*q_bit.dt()*1e-5 == p_p - (f_d/3600)*q_bit**2 + Ro_d*g*h_bit/1e5 - p_bit)
m.Equation(Vd*p_p.dt()/Beta_d == q_p-q_bit)
m.Equation(h_bit.dt() == ROP + 0*h_bit)

# Options
m.options.solver = 1

# Calculate starting conditions
m.options.imode = 3
m.solve()

# Print solution
print('------------------------------------------------')
print('Pressure at Pump [bar]', p_p.value)
print('Pressure at Choke Valve [bar]', p_c.value)
print('Bit pressure [bar]', p_bit.value)
print('Flow Rate through Bit [m^3/min] ', q_bit.value)
print('Flow Rate through Choke [m^3/min]', q_choke.value)
print('Bit Height [m]', h_bit.value)
print('------------------------------------------------')
print('')

# Simulation time
tf = 300.0  # final time (sec)
st = 2.0   # simulation time intervals
nt = int(tf/st)+1 # simulation time points
m.time = np.linspace(0,tf,nt)/60.0

# Configure choke valve step
zc = np.ones(nt)*30.0
zc[50:] = 25.0  # change to 25% open
zc[100:] = 20.0 # change to 20% open
z_choke.value = zc

# Configure pump ramp
q_pump = np.ones(nt)*2.0
# ramp up
for i in range(5,len(q_pump)):
    if q_pump[i-1]<=2.95:
        q_pump[i] = q_pump[i-1]+0.05
    else:
        q_pump[i] = 3.0
q_p.value = q_pump
m.options.imode = 4 # dynamic simulation
m.solve()

plt.figure(1)

plt.subplot(4,1,1)
plt.plot(m.time,q_p,'b-',label='Mud Pump Flow')
plt.plot(m.time,q_bit,'g:',label='Bit Mud Flow')
plt.plot(m.time,q_choke,'r--',label='Choke Mud Flow')
plt.ylabel(r'Flow ($m^3/min$)')
plt.legend(loc='best')

plt.subplot(4,1,2)
plt.plot(m.time,z_choke,'k-',label='Choke Opening (%)')
plt.ylabel('Choke (%)')
plt.legend(loc='best')

plt.subplot(4,1,3)
plt.plot(m.time,p_bit,'r-',label='Bit Pressure (bar)')
plt.ylabel('Press (bar)')
plt.legend(loc='best')

plt.subplot(4,1,4)
plt.plot(m.time,p_p,'r:',label='Pump Pressure (bar)')
plt.plot(m.time,p_c,'b--',label='Choke Pressure (bar)')
plt.legend(loc='best')
plt.ylabel('Press (bar)')
plt.xlabel('Time (min)')
plt.show()

