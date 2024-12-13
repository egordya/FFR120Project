import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend suitable for headless environments
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


COLOR_RED = "#E53D00"


class HeadLessMeasurementAndPlotter:
    def __init__(self, output_dir="plots"):
        """
        Initialize the headless measurement and plotter.

        Parameters:
            output_dir (str): Directory to save the plot images.
        """
        self.output_dir = output_dir

    def plot_velocity_distribution(self, velocities_acc, velocities_no_acc, simulation_params, percent_faster, percent_slower):
        """
        Plot the distribution of car velocities for both ACC and Non-ACC cars, including simulation parameters and driver percentages.

        Parameters:
            velocities_acc (array-like): Velocities of Adaptive Cruise Control Cars.
            velocities_no_acc (array-like): Velocities of Human Driver Cars (No ACC).
            simulation_params (dict): Dictionary containing simulation parameters (L, N, vmax, p_fault, p_slow, rho).
            percent_faster (float): Percentage of Non-ACC cars that are faster.
            percent_slower (float): Percentage of Non-ACC cars that are slower.
        """
        L = simulation_params['L']
        N = simulation_params['N']
        vmax = simulation_params['vmax']
        p_fault = simulation_params['p_fault']
        p_slow = simulation_params['p_slow']
        rho = simulation_params['rho']

        plt.figure(figsize=(8, 6))
        bins = range(0, vmax + 3)

        # Plot histograms
        plt.hist(velocities_acc, bins=bins, alpha=0.5, label='Adaptive Cruise Control Cars', color='dodgerblue', edgecolor='black')
        plt.hist(velocities_no_acc, bins=bins, alpha=0.5, label='Human Driver Cars (No ACC)', color='salmon', edgecolor='black')

        # Labels and Title
        plt.xlabel('Velocity (cells/step)')
        plt.ylabel('Number of Cars')
        plt.title(
            f'Velocity Distribution\n'
            f'L={L}, N={N}, vmax={vmax}, p_fault={p_fault}, p_slow={p_slow}, rho={rho:.2f}\n'
            f'Faster Drivers: {percent_faster:.2f}%, Slower Drivers: {percent_slower:.2f}%'
        )
        plt.legend()
        plt.xticks(bins)  # Ensure x-ticks are integers
        plt.xlim(0, 6)  # Set x-axis limits from 0 to 6
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/velocity_distribution.png")
        plt.close()

    def plot_velocity_distribution_with_params(self, velocities_no_acc_dict, p_fault_values, p_slow_values):
        """
        Plot how p_fault and p_slow affect the distribution of car velocities for Human Driver Cars (No ACC).

        Parameters:
            velocities_no_acc_dict (dict): A dictionary where keys might be (p_fault, p_slow) tuples and values are arrays of velocities.
                                           Example: {(0.1,0.5): [vel_array], (0.2,0.5): [vel_array], ...}
            p_fault_values (array-like): Different p_fault values tested.
            p_slow_values (array-like): Different p_slow values tested.

        This function creates multiple plots or a combined plot to show how distributions change with these parameters.
        """
        # For simplicity, let's create one plot per (p_fault, p_slow) combination.
        for (pf, ps), vel_array in velocities_no_acc_dict.items():
            plt.figure(figsize=(6,4))
            bins = range(0, int(np.max(vel_array))+2)
            plt.hist(vel_array, bins=bins, alpha=0.7, color='salmon')
            plt.xlabel('Velocity (cells/step)')
            plt.ylabel('Number of Cars')
            plt.title(f'Velocity Distribution (Human Driver, p_fault={pf}, p_slow={ps})')
            plt.tight_layout()
            plt.savefig(f"{self.output_dir}/velocity_distribution_no_acc_pfault{pf}_pslow{ps}.png")
            plt.close()

    def plot_flow_rate(self, flow_rate_acc, flow_rate_no_acc, time_steps):
        """
        Plot the flow rate for both types of cars over time.

        Parameters:
            flow_rate_acc (array-like): Flow rate over time for Adaptive Cruise Control Cars.
            flow_rate_no_acc (array-like): Flow rate over time for Human Driver Cars (No ACC).
            time_steps (array-like): Corresponding time steps or simulation steps.
        """
        plt.figure(figsize=(6,4))
        plt.plot(time_steps, flow_rate_acc, label='Adaptive Cruise Control Cars', color='dodgerblue')
        plt.plot(time_steps, flow_rate_no_acc, label='Human Driver Cars (No ACC)', color='salmon')
        plt.xlabel('Time (steps)')
        plt.ylabel('Flow Rate (cars/min or cars/step)')
        plt.title('Flow Rate Over Time')
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/flow_rate_comparison.png")
        plt.close()

    def plot_additional_metrics(self, jam_lengths_acc, jam_lengths_no_acc, stops_acc, stops_no_acc):
        """
        Suggestion: Additional metrics can be visualized. For example:
        - Jam length distribution over time or final jam lengths.
        - Number of stops distribution for both ACC and Non-ACC cars.

        Parameters:
            jam_lengths_acc (array-like): Jam lengths recorded over time for ACC.
            jam_lengths_no_acc (array-like): Jam lengths recorded over time for Non-ACC.
            stops_acc (array-like): Total stops per car for ACC cars.
            stops_no_acc (array-like): Total stops per car for Non-ACC cars.
        """

        # Example: Plot jam length over time
        plt.figure(figsize=(6,4))
        steps = range(len(jam_lengths_acc))
        plt.plot(steps, jam_lengths_acc, label='Adaptive Cruise Control Cars', color='dodgerblue')
        plt.plot(steps, jam_lengths_no_acc, label='Human Driver Cars (No ACC)', color='salmon')
        plt.xlabel('Time (steps)')
        plt.ylabel('Jam Length (cells)')
        plt.title('Jam Length Over Time')
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/jam_length_over_time.png")
        plt.close()

        # Example: Histogram of stops
        plt.figure(figsize=(8, 6))  # Increased figure size for better visibility

        # Plotting KDE for Adaptive Cruise Control Cars
        sns.kdeplot(
            stops_acc,
            label='Adaptive Cruise Control Cars',
            color='dodgerblue',
            shade=True,
            alpha=0.5,
            bw_adjust=0.5,
            clip=(0, None)
        )

        # Plotting KDE for Human Driver Cars (No ACC)
        sns.kdeplot(
            stops_no_acc,
            label='Human Driver Cars (No ACC)',
            color='salmon',
            shade=True,
            alpha=0.5,
            bw_adjust=0.5,
            clip=(0, None)
        )

        plt.xlabel('Number of Stops per Car')
        plt.ylabel('Density')
        plt.title('Stop Distribution')
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/stops_distribution_density.png")
        plt.close()


    def plot_distance_traveled_distribution(self, d_acc, d_no_acc, L, N, vmax, p_fault, p_slow, rho):
        plt.figure(figsize=(6,4))
        bins = np.linspace(0, max(max(d_acc), max(d_no_acc))+1, 20)
        plt.hist(d_acc, bins=bins, alpha=0.5, label='ACC Cars', color='dodgerblue')
        plt.hist(d_no_acc, bins=bins, alpha=0.5, label='Non-ACC Cars', color='salmon')
        plt.xlabel('Total Distance Traveled (cells)')
        plt.ylabel('Number of Cars')
        plt.title(f'Distance Traveled Distribution\n(L={L}, N={N}, vmax={vmax}, p_fault={p_fault}, p_slow={p_slow}, rho={rho:.2f})')
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/distance_traveled_distribution.png")
        plt.close()

    def plot_fraction_stopped_over_time(self, time_steps, f_acc, f_no_acc, L, N, vmax, p_fault, p_slow, rho):
        plt.figure(figsize=(6,4))
        plt.plot(time_steps, f_acc, label='ACC Cars', color='dodgerblue')
        plt.plot(time_steps, f_no_acc, label='Non-ACC Cars', color='salmon')
        plt.xlabel('Time (steps)')
        plt.ylabel('Fraction of Stopped Cars')
        plt.title(f'Fraction of Stopped Cars Over Time\n(L={L}, N={N}, vmax={vmax}, p_fault={p_fault}, p_slow={p_slow}, rho={rho:.2f})')
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/fraction_stopped_over_time.png")
        plt.close()

    # (6) Delay Over Time
    def plot_delay_over_time(self, time_steps, delay_acc, delay_no_acc, L, N, vmax, p_fault, p_slow, rho):
        plt.figure(figsize=(6,4))
        plt.plot(time_steps, delay_acc, label='ACC Cars Delay', color='dodgerblue')
        plt.plot(time_steps, delay_no_acc, label='Non-ACC Cars Delay', color='salmon')
        plt.xlabel('Time (steps)')
        plt.ylabel('Average Delay (%)')
        plt.yscale('linear')
        plt.title(f'Delay Over Time\n(L={L}, N={N}, vmax={vmax}, p_fault={p_fault}, p_slow={p_slow}, rho={rho:.2f})')
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/delay_over_time.png")
        plt.close()

    # (7) Stop-Start Frequency Distribution
    def plot_stop_start_frequency_distribution(self, ss_acc, ss_no_acc, L, N, vmax, p_fault, p_slow, rho):
        plt.figure(figsize=(8, 6))  # Increased figure size for better visibility

        # Plotting KDE for ACC Cars
        sns.kdeplot(
            ss_acc,
            label='ACC Cars',
            color='dodgerblue',
            shade=True,
            alpha=0.5,
            bw_adjust=0.5,  # Adjust bandwidth for smoother curves
            clip=(0, None)  # Ensure KDE starts at 0
        )

        # Plotting KDE for Non-ACC Cars
        sns.kdeplot(
            ss_no_acc,
            label='Non-ACC Cars',
            color='salmon',
            shade=True,
            alpha=0.5,
            bw_adjust=0.5,
            clip=(0, None)
        )

        plt.xlabel('Stop-Start Transitions per Car')
        plt.ylabel('Density')
        plt.title(
            f'Stop-Start Frequency Distribution\n'
            f'(L={L}, N={N}, vmax={vmax}, p_fault={p_fault}, p_slow={p_slow}, rho={rho:.2f})'
        )
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/stop_start_frequency_distribution_density.png")
        plt.close()

    def plot_velocity_cdf(self, velocities_acc, velocities_no_acc, L, N, vmax, p_fault, p_slow, rho):
        """
        Plot the CDF of velocities for ACC and Non-ACC cars.

        Parameters:
            velocities_acc (array-like): Velocities of Adaptive Cruise Control Cars.
            velocities_no_acc (array-like): Velocities of Human Driver Cars (No ACC).
            L, N, vmax, p_fault, p_slow, rho: Simulation parameters for title and annotation.
        """
        plt.figure(figsize=(6, 4))

        # Compute CDF for ACC
        sorted_acc = np.sort(velocities_acc)
        cdf_acc = np.arange(1, len(sorted_acc) + 1) / len(sorted_acc)

        # Compute CDF for Non-ACC
        sorted_no_acc = np.sort(velocities_no_acc)
        cdf_no_acc = np.arange(1, len(sorted_no_acc) + 1) / len(sorted_no_acc)

        # Plot CDF
        plt.plot(sorted_acc, cdf_acc, label='ACC Cars', color='dodgerblue')
        plt.plot(sorted_no_acc, cdf_no_acc, label='Non-ACC Cars', color='salmon')

        # Match x-axis limits and ticks with velocity distribution plot
        bins = range(0, vmax + 3)  # Ensure same bins as in velocity distribution
        plt.xticks(bins)  # Set x-ticks to match
        plt.xlim(0, vmax + 2)  # Ensure x-axis limits are the same

        # Labels and Title
        plt.xlabel('Velocity (cells/step)')
        plt.ylabel('Cumulative Probability')
        plt.title(
            f'CDF of Velocities\n(L={L}, N={N}, vmax={vmax}, p_fault={p_fault}, p_slow={p_slow}, rho={rho:.2f})'
        )
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/velocity_cdf.png")
        plt.close()
