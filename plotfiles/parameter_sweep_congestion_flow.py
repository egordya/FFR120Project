# plot_congestion_vs_flow.py

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend suitable for headless environments
import matplotlib.pyplot as plt

from run_simulation import run_simulation

def parameter_sweep_congestion_flow(
    L=120,                     # Road length
    vmax=4,                    # Maximum speed
    p_fault=0.1,               # Probability of random slowdown
    p_slow=0.5,                # Probability of slow-to-start behavior
    steps=1000,                # Number of simulation steps
    prob_faster=0.10,          # Probability of faster drivers
    prob_slower=0.20,          # Probability of slower drivers
    prob_normal=0.70,          # Probability of normal drivers
    headless=True,             # Run simulation in headless mode
    output_csv="congestion_flow_stats.csv",  # Output CSV file
    output_plot="congestion_vs_flow.png"      # Output plot image
):
    """
    Perform a parameter sweep over different rho values and plot the relationship
    between congestion percentage and average flow rate.

    Parameters:
        L (int): Road length.
        vmax (int): Maximum speed of cars.
        p_fault (float): Probability of random slowdown.
        p_slow (float): Probability of slow-to-start behavior.
        steps (int): Number of simulation steps.
        prob_faster (float): Probability of faster drivers.
        prob_slower (float): Probability of slower drivers.
        prob_normal (float): Probability of normal drivers.
        headless (bool): Whether to run the simulation without visualization.
        output_csv (str): Filename for the output CSV.
        output_plot (str): Filename for the output plot.
    """
    # Define rho range from 0 to 1
    rho_values = np.linspace(0.05, 1.0, 20)  # Avoid rho=0 to prevent division by zero
    N_values = (rho_values * (L / 2)).astype(int)  # N = rho * (L/2)

    # Lists to store results
    results = []

    for idx, (rho, N) in enumerate(zip(rho_values, N_values)):
        print(f"Running simulation {idx+1}/{len(rho_values)}: rho={rho:.2f}, N={N}")

        # Run simulation
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
            headless=headless
        )

        # Calculate average flow rates
        flow_rate_acc = simulation_data['flow_rate_acc']
        flow_rate_no_acc = simulation_data['flow_rate_no_acc']
        mean_flow_rate_acc = np.mean(flow_rate_acc) if flow_rate_acc else 0
        mean_flow_rate_no_acc = np.mean(flow_rate_no_acc) if flow_rate_no_acc else 0

        # Calculate congestion percentage (average fraction stopped)
        fraction_stopped_road1 = simulation_data['fraction_stopped_road1']
        fraction_stopped_road2 = simulation_data['fraction_stopped_road2']
        mean_fraction_stopped_road1 = np.mean(fraction_stopped_road1) if fraction_stopped_road1 else 0
        mean_fraction_stopped_road2 = np.mean(fraction_stopped_road2) if fraction_stopped_road1 else 0

        # Store the results
        results.append({
            'rho': rho,
            'N': N,
            'mean_flow_rate_acc': mean_flow_rate_acc,
            'mean_flow_rate_no_acc': mean_flow_rate_no_acc,
            'mean_fraction_stopped_road1': mean_fraction_stopped_road1,
            'mean_fraction_stopped_road2': mean_fraction_stopped_road2
        })

    # Convert results to DataFrame
    df = pd.DataFrame(results)

    # Save to CSV
    df.to_csv(output_csv, index=False)
    print(f"Results saved to {output_csv}")

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.scatter(df['mean_fraction_stopped_road1'], df['mean_flow_rate_acc'],
                label='ACC Cars', color='dodgerblue', alpha=0.7)
    plt.scatter(df['mean_fraction_stopped_road2'], df['mean_flow_rate_no_acc'],
                label='Non-ACC Cars', color='salmon', alpha=0.7)

    plt.xlabel('Mean Congestion Percentage (Fraction of Stopped Cars)')
    plt.ylabel('Mean Flow Rate (cars/step)')
    plt.title('Flow Rate vs. Congestion Percentage')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_plot, dpi = 300)
    plt.close()
    print(f"Plot saved to {output_plot}")

if __name__ == "__main__":
    parameter_sweep_congestion_flow()
