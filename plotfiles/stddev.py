import numpy as np
import pandas as pd
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from run_simulation import run_simulation


def main():
    # Parameters
    runs = 100  # Number of independent simulation runs to average over
    steps = 1000
    L = 120
    N = 30
    vmax = 4
    p_fault = 0.1
    p_slow = 0.5
    prob_faster = 0.10
    prob_slower = 0.20
    prob_normal = 0.70

    rho  = N / (L / 2)

    # Lists to store results from each run
    fraction_stopped_road1_all = []
    fraction_stopped_road2_all = []
    flow_rate_acc_all = []
    flow_rate_no_acc_all = []
    time_steps = None

    # Run simulations multiple times
    for i in range(runs):
        cars_road1, cars_road2, simulation_data = run_simulation(
            L=L, N=N, vmax=vmax,
            p_fault=p_fault, p_slow=p_slow,
            steps=steps, prob_faster=prob_faster,
            prob_slower=prob_slower, prob_normal=prob_normal,
            headless=True
        )

        if time_steps is None:
            time_steps = simulation_data['time_steps']

        fraction_stopped_road1_all.append(simulation_data['fraction_stopped_road1'])
        fraction_stopped_road2_all.append(simulation_data['fraction_stopped_road2'])
        flow_rate_acc_all.append(simulation_data['flow_rate_acc'])
        flow_rate_no_acc_all.append(simulation_data['flow_rate_no_acc'])

    # Convert lists to arrays for easy mean/std computations
    fraction_stopped_road1_all = np.array(fraction_stopped_road1_all)  # shape: (runs, steps)
    fraction_stopped_road2_all = np.array(fraction_stopped_road2_all)
    flow_rate_acc_all = np.array(flow_rate_acc_all)
    flow_rate_no_acc_all = np.array(flow_rate_no_acc_all)

    # Compute mean and std
    fraction_stopped_road1_mean = fraction_stopped_road1_all.mean(axis=0)
    fraction_stopped_road1_std = fraction_stopped_road1_all.std(axis=0)

    fraction_stopped_road2_mean = fraction_stopped_road2_all.mean(axis=0)
    fraction_stopped_road2_std = fraction_stopped_road2_all.std(axis=0)

    flow_rate_acc_mean = flow_rate_acc_all.mean(axis=0)
    flow_rate_acc_std = flow_rate_acc_all.std(axis=0)

    flow_rate_no_acc_mean = flow_rate_no_acc_all.mean(axis=0)
    flow_rate_no_acc_std = flow_rate_no_acc_all.std(axis=0)

    # Create dataframes for CSV output
    fraction_stopped_df = pd.DataFrame({
        'time_step': time_steps,
        'fraction_stopped_road1_mean': fraction_stopped_road1_mean,
        'fraction_stopped_road1_std': fraction_stopped_road1_std,
        'fraction_stopped_road2_mean': fraction_stopped_road2_mean,
        'fraction_stopped_road2_std': fraction_stopped_road2_std
    })

    flow_rate_df = pd.DataFrame({
        'time_step': time_steps,
        'flow_rate_acc_mean': flow_rate_acc_mean,
        'flow_rate_acc_std': flow_rate_acc_std,
        'flow_rate_no_acc_mean': flow_rate_no_acc_mean,
        'flow_rate_no_acc_std': flow_rate_no_acc_std
    })

    # Save CSV files
    fraction_stopped_df.to_csv("fraction_stopped_stats.csv", index=False)
    flow_rate_df.to_csv("flow_rate_stats.csv", index=False)

    # Plot fraction of stopped cars mean and std
    # Plot fraction of stopped cars mean and std
    plt.figure(figsize=(8, 5))
    plt.plot(time_steps, fraction_stopped_road1_mean, label='ACC Cars Mean', color='dodgerblue')
    plt.fill_between(time_steps,
                     fraction_stopped_road1_mean - fraction_stopped_road1_std,
                     fraction_stopped_road1_mean + fraction_stopped_road1_std,
                     alpha=0.3, color='lightskyblue')

    plt.plot(time_steps, fraction_stopped_road2_mean, label='Non-ACC Cars Mean', color='salmon')
    plt.fill_between(time_steps,
                     fraction_stopped_road2_mean - fraction_stopped_road2_std,
                     fraction_stopped_road2_mean + fraction_stopped_road2_std,
                     alpha=0.3, color='lightsalmon')

    plt.xlabel('Time (steps)')
    plt.ylabel('Fraction of Stopped Cars')
    plt.title(
        f'Fraction of Stopped Cars Over Time (Mean ± Std)\n'
        f'(L={L}, N={N}, vmax={vmax}, p_fault={p_fault}, p_slow={p_slow}, rho={rho:.2f}, {runs} Simulation Runs)'
    )
    plt.legend()
    plt.tight_layout()
    plt.savefig("fraction_stopped_mean_std_trans.png", dpi=300, transparent=True)
    plt.close()

    # Plot flow rate mean and std
    plt.figure(figsize=(8, 5))
    plt.plot(time_steps, flow_rate_acc_mean, label='ACC Cars Mean Flow Rate', color='dodgerblue')
    plt.fill_between(time_steps,
                     flow_rate_acc_mean - flow_rate_acc_std,
                     flow_rate_acc_mean + flow_rate_acc_std,
                     alpha=0.3, color='lightskyblue')

    plt.plot(time_steps, flow_rate_no_acc_mean, label='Non-ACC Mean Flow Rate', color='salmon')
    plt.fill_between(time_steps,
                     flow_rate_no_acc_mean - flow_rate_no_acc_std,
                     flow_rate_no_acc_mean + flow_rate_no_acc_std,
                     alpha=0.3, color='lightsalmon')

    plt.xlabel('Time (steps)')
    plt.ylabel('Flow Rate (cars/step)')
    plt.title(
        f'Flow Rate Over Time (Mean ± Std)\n'
        f'(L={L}, N={N}, vmax={vmax}, p_fault={p_fault}, p_slow={p_slow}, rho={rho:.2f}, {runs} Simulation Runs)'
    )
    plt.legend()
    plt.tight_layout()
    plt.savefig("flow_rate_mean_std_trans.png", dpi=300, transparent=True)
    plt.close()
    print("Analysis completed. CSV files and plots saved.")


if __name__ == "__main__":
    main()
