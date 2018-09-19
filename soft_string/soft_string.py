from gekko import GEKKO
import numpy as np
import matplotlib.pyplot as plt

# Initialize Model
m = GEKKO()

n = 43  # number of discretized segments
ks = m.Param(35950)
kb = m.Param(204020)
js = m.Param(3.2021)
jb = m.Param(15.8480)
ds = m.Param(0.0271)
db = m.Param(0.0266)
vtd = m.Param(10)

v = [m.Var(0) for i in range(n)] # velocity
d = [m.Var(0) for i in range(n)] # acceleration

df = []  # rotational velocity difference
for i in range(n-1):
    df.append(m.Intermediate(v[i]-v[i+1]))

m.Equation(js*v[0].dt()==ds*ks*(vtd-v[0])+ks*d[0]-ds*ks*df[0]-ks*d[1])
for i in range(1,n-1):
    m.Equation(js*v[i].dt()==ds*ks*df[i-1]+ks*d[i]-ds*ks*df[i]-ks*d[i+1])
p1 = m.Intermediate(db*kb*df[n-2]+kb*d[n-1])
den = m.Intermediate(v[n-1]**2+0.2**2)
p2 = m.Intermediate(-1764*(v[n-1]/m.sqrt(den)+(1.5*0.2*v[n-1])/den))
m.Equation(jb*v[n-1].dt()==p1+p2-0.28*v[n-1]*(v[n-1]/31.4-1))
m.Equation(d[0].dt()==vtd-v[0])
for i in range(1,n):
    m.Equation(d[i].dt()==df[i-1])

m.options.imode = 4
m.options.nodes = 3
m.options.csv_read = 1
m.options.dbs_read = 1

m.time = np.linspace(0,10,101)

m.solve(disp=False)

plt.figure(1)
plt.subplot(2,1,1)
for i in range(n):
    plt.plot(m.time,v[i])
plt.ylabel(r'Rot Rate ($rad/s$)')
plt.legend(['Top Drive','Section 1','Section 2', 'etc'],loc='best')

plt.subplot(2,1,2)
for i in range(n):
    plt.plot(m.time,d[i])
plt.ylabel(r'Accel ($rad/s^2$)')
plt.legend(['Top Drive','Section 1','Section 2', 'etc'],loc='best')
plt.show()
