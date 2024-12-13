import numpy as np
import matplotlib

from run_simulation import run_simulation

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from random import seed
seed(1)

def parameter_sweep_flow_rate(L=120, vmax=4, p_fault=0.1, p_slow=0.5, steps=1000, prob_faster=0.10, prob_slower=0.20, prob_normal=0.70):
    # For rho to vary from 0 to 1:
    # rho = N/(L/2) => N = rho*(L/2)
    # For rho in [0, 1], N in [0, L/2].
    max_N = int(L/2)  # when rho=1
    rho_values = []
    flow_rate_acc_values = []
    flow_rate_no_acc_values = []

    for N in range(0, max_N+1, 5):  # Adjust the step size if needed (e.g., every 5 cars)
        cars_road1, cars_road2, simulation_data = run_simulation(
            L=L,
            N=N,
            vmax=vmax,
            p_fault=p_fault,
            p_slow=p_slow,
            steps=steps,
            prob_faster=prob_faster,
            prob_slower=prob_slower,
            prob_normal=prob_normal,
            headless=True
        )

        # Extract flow rates
        flow_rate_acc = simulation_data['flow_rate_acc']  # array of flow rates over time
        flow_rate_no_acc = simulation_data['flow_rate_no_acc']  # array of flow rates over time
        # Compute mean flow rate to represent the steady-state flow
        mean_flow_rate_acc = np.mean(flow_rate_acc)
        mean_flow_rate_no_acc = np.mean(flow_rate_no_acc)

        # Compute rho
        rho = simulation_data['rho']  # This should be defined as N/(L/2) by run_simulation
        rho_values.append(rho)
        flow_rate_acc_values.append(mean_flow_rate_acc)
        flow_rate_no_acc_values.append(mean_flow_rate_no_acc)

    # Plot the results
    plt.figure(figsize=(8,6))
    plt.plot(rho_values, flow_rate_acc_values, '-o', label='ACC Cars', color='dodgerblue')
    plt.plot(rho_values, flow_rate_no_acc_values, '-o', label='Non-ACC Cars', color='salmon')
    plt.xlabel('ρ (Traffic Density)')
    plt.ylabel('Mean Flow Rate (cars/step)')
    plt.title(f'Flow Rate vs. Density (L={L}, steps={steps}, vmax={vmax}, p_fault={p_fault}, p_slow={p_slow})')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("flow_rate_vs_rho.png", dpi = 300)
    plt.close()

    print("Parameter sweep completed. Plot saved to 'flow_rate_vs_rho.png'.")

if __name__ == "__main__":
    parameter_sweep_flow_rate()
