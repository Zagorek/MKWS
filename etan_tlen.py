import cantera as ct
import numpy as np
import matplotlib.pyplot as plt

def combust(T: float, P: float, spcies_dict: dict, reactor: str, dt: float= 0.0005, till_ignition: bool=True):
    gas = ct.Solution('gri30.yaml')
    gas.TPX = T, P, spcies_dict
    # Typ reaktora wg symulacji
    if reactor == 'constant temperature':
        r = ct.IdealGasReactor(gas)
    
    elif reactor == 'constant pressure':
        r = ct.IdealGasConstPressureReactor(gas)
    
    else:
        raise TypeError(f"Improper reactor type '{reactor}'")
    
    sim = ct.ReactorNet([r])
    # Stany
    states = ct.SolutionArray(gas, extra=['time_in_ms', 'time_in_sec'])

    # Symulacja dla 10 sec = dt*n_steps
    simulation_time = 10
    # dt rozmiar kroku
    n_steps = int(simulation_time/dt)
    ignition_delay = 0.0
    
    # Warunek sprawdzający, czy doszło do samozapłonu 

    ignited = False
    
    time = 0.0
    for n in range(n_steps):
        time += dt
        sim.advance(time)
        states.append(r.thermo.state, time_in_sec= time, time_in_ms= time*1e3)
        
        if ignited == False:
            if states.T[n] >= (T + 400):
                ignition_delay = time
                ignited = True
                if till_ignition == True:
                    break

    return gas, states, ignition_delay

# PART I-const temperature
fig1, axs = plt.subplots(2,1, figsize=(10, 10))

igd_lst = []
P = np.linspace(1,4,7)
for t in P:
    _, states, igd = combust(1100, t*ct.one_atm, {'C2H6':1, 'O2':3.5}, 'constant temperature', dt= 1e-4)
    axs[0].plot(states.time_in_ms, states.T, '.-', label= f'{t: .3} atm, I.D. = {igd*1000: .5} ms')
    igd_lst.append(igd)

axs[0].set_xlabel('Time [ms]$\longrightarrow$')
axs[0].set_ylabel("Flame Temperature [K]$\longrightarrow$")
axs[0].grid(linestyle='-.')
axs[0].legend()

axs[1].plot(np.array(igd_lst)*1000, P, '.-')
axs[1].set_xlabel('Auto-ignition time [ms]$\longrightarrow$')
axs[1].set_ylabel("Pressure [atm]$\longrightarrow$")
axs[1].grid(linestyle='-.')

fig1.suptitle(f"Auto-ignition of ethane-oxygen at 1100 K and pressure variation")

# PART II-const pressure
fig2, axs = plt.subplots(2,1, figsize=(10, 10))

igd_lst = []
T = np.linspace(1000, 1200, 6)
for t in T:
    _, states, igd = combust(t, 3*ct.one_atm, {'C2H6':1, 'O2':3.5}, 'constant pressure')
    axs[0].plot(states.time_in_ms, states.T, '.-', label= f'{t} K, I.D. = {igd*1000: .5} ms')
    igd_lst.append(igd)

axs[0].set_xlabel('Time [ms]$\longrightarrow$')
axs[0].set_ylabel("Flame Temperature [K]$\longrightarrow$")
axs[0].grid(linestyle='-.')
axs[0].legend()

axs[1].plot(np.array(igd_lst)*1000, T, '.-')
axs[1].set_xlabel('Auto-ignition time [ms]$\longrightarrow$')
axs[1].set_ylabel("Initial temperature [K]$\longrightarrow$")
axs[1].grid(linestyle='-.')

fig2.suptitle(f"Auto-ignition of ethane-oxygen at 3 atm and initial temperature variation")

plt.show()