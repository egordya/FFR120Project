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
        L = simulation_params['L']
        N = simulation_params['N']
        vmax = simulation_params['vmax']
        p_fault = simulation_params['p_fault']
        p_slow = simulation_params['p_slow']
        rho = simulation_params['rho']

        plt.figure(figsize=(8, 6))
        bins = range(0, vmax + 3)

        plt.hist(velocities_acc, bins=bins, alpha=0.5, label='ACC Cars', color='dodgerblue', edgecolor='black')
        plt.hist(velocities_no_acc, bins=bins, alpha=0.5, label='Non-ACC Cars', color='salmon', edgecolor='black')

        plt.xlabel('Velocity (cells/step)')
        plt.ylabel('Number of Cars')
        plt.title(
            f'Velocity Distribution\n'
            f'(L={L}, N={N}, vmax={vmax}, p_fault={p_fault}, p_slow={p_slow}, rho={rho:.2f})\n'
            f'Faster Drivers: {percent_faster:.2f}%, Slower Drivers: {percent_slower:.2f}%'
        )
        plt.legend()
        plt.xticks(bins)
        plt.xlim(0, vmax + 2)
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/velocity_distribution.png", dpi=300)
        plt.close()

    def plot_flow_rate(self, flow_rate_acc, flow_rate_no_acc, time_steps, simulation_params):
        L = simulation_params['L']
        N = simulation_params['N']
        vmax = simulation_params['vmax']
        p_fault = simulation_params['p_fault']
        p_slow = simulation_params['p_slow']
        rho = simulation_params['rho']

        plt.figure(figsize=(6,4))
        plt.plot(time_steps, flow_rate_acc, label='ACC Cars', color='dodgerblue')
        plt.plot(time_steps, flow_rate_no_acc, label='Non-ACC Cars', color='salmon')
        plt.xlabel('Time (steps)')
        plt.ylabel('Flow Rate (cars/step)')
        plt.title(
            f'Flow Rate Over Time\n(L={L}, N={N}, vmax={vmax}, p_fault={p_fault}, p_slow={p_slow}, rho={rho:.2f})'
        )
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/flow_rate_comparison.png", dpi=300)
        plt.close()

    def plot_additional_metrics(self, jam_lengths_acc, jam_lengths_no_acc, stops_acc, stops_no_acc, simulation_params):
        L = simulation_params['L']
        N = simulation_params['N']
        vmax = simulation_params['vmax']
        p_fault = simulation_params['p_fault']
        p_slow = simulation_params['p_slow']
        rho = simulation_params['rho']

        # Jam Length Over Time
        plt.figure(figsize=(6, 4))
        steps = range(len(jam_lengths_acc))
        plt.plot(steps, jam_lengths_acc, label='ACC Cars', color='dodgerblue')
        plt.plot(steps, jam_lengths_no_acc, label='Non-ACC Cars', color='salmon')
        plt.xlabel('Time (steps)')
        plt.ylabel('Jam Length (cells)')
        plt.title(
            f'Jam Length Over Time\n(L={L}, N={N}, vmax={vmax}, p_fault={p_fault}, p_slow={p_slow}, rho={rho:.2f})'
        )
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/jam_length_over_time.png", dpi=300)
        plt.close()

        # Stop Distribution (KDE)
        plt.figure(figsize=(8, 6))
        sns.kdeplot(
            stops_acc,
            label='ACC Cars',
            color='dodgerblue',
            shade=True,
            alpha=0.5,
            bw_adjust=0.5,
            clip=(0, None)
        )

        sns.kdeplot(
            stops_no_acc,
            label='Non-ACC Cars',
            color='salmon',
            shade=True,
            alpha=0.5,
            bw_adjust=0.5,
            clip=(0, None)
        )

        plt.xlabel('Number of Stops per Car')
        plt.ylabel('Density')
        plt.title(
            f'Stop Distribution\n(L={L}, N={N}, vmax={vmax}, p_fault={p_fault}, p_slow={p_slow}, rho={rho:.2f})'
        )
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/stops_distribution_density.png", dpi=300)
        plt.close()

    # Updated to use seaborn KDE similar to the stop distribution
    def plot_distance_traveled_distribution(self, d_acc, d_no_acc, simulation_params):
        L = simulation_params['L']
        N = simulation_params['N']
        vmax = simulation_params['vmax']
        p_fault = simulation_params['p_fault']
        p_slow = simulation_params['p_slow']
        rho = simulation_params['rho']

        plt.figure(figsize=(8, 6))
        sns.kdeplot(
            d_acc,
            label='ACC Cars',
            color='dodgerblue',
            shade=True,
            alpha=0.5,
            bw_adjust=0.5,
            clip=(0, None)
        )

        sns.kdeplot(
            d_no_acc,
            label='Non-ACC Cars',
            color='salmon',
            shade=True,
            alpha=0.5,
            bw_adjust=0.5,
            clip=(0, None)
        )

        plt.xlabel('Total Distance Traveled (cells)')
        plt.ylabel('Density')
        plt.title(
            f'Distance Traveled Distribution\n(L={L}, N={N}, vmax={vmax}, p_fault={p_fault}, p_slow={p_slow}, rho={rho:.2f})'
        )
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/distance_traveled_distribution_kde.png", dpi=300)
        plt.close()

    def plot_fraction_stopped_over_time(self, time_steps, f_acc, f_no_acc, simulation_params):
        L = simulation_params['L']
        N = simulation_params['N']
        vmax = simulation_params['vmax']
        p_fault = simulation_params['p_fault']
        p_slow = simulation_params['p_slow']
        rho = simulation_params['rho']

        plt.figure(figsize=(6,4))
        plt.plot(time_steps, f_acc, label='ACC Cars', color='dodgerblue')
        plt.plot(time_steps, f_no_acc, label='Non-ACC Cars', color='salmon')
        plt.xlabel('Time (steps)')
        plt.ylabel('Fraction of Stopped Cars')
        plt.title(
            f'Fraction of Stopped Cars Over Time\n(L={L}, N={N}, vmax={vmax}, p_fault={p_fault}, p_slow={p_slow}, rho={rho:.2f})'
        )
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/fraction_stopped_over_time.png", dpi=300)
        plt.close()

    def plot_delay_over_time(self, time_steps, delay_acc, delay_no_acc, simulation_params):
        L = simulation_params['L']
        N = simulation_params['N']
        vmax = simulation_params['vmax']
        p_fault = simulation_params['p_fault']
        p_slow = simulation_params['p_slow']
        rho = simulation_params['rho']

        plt.figure(figsize=(6,4))
        plt.plot(time_steps, delay_acc, label='ACC Cars Delay', color='dodgerblue')
        plt.plot(time_steps, delay_no_acc, label='Non-ACC Cars Delay', color='salmon')
        plt.xlabel('Time (steps)')
        plt.ylabel('Average Delay (%)')
        plt.title(
            f'Delay Over Time\n(L={L}, N={N}, vmax={vmax}, p_fault={p_fault}, p_slow={p_slow}, rho={rho:.2f})'
        )
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/delay_over_time.png", dpi=300)
        plt.close()

    def plot_stop_start_frequency_distribution(self, ss_acc, ss_no_acc, simulation_params):
        L = simulation_params['L']
        N = simulation_params['N']
        vmax = simulation_params['vmax']
        p_fault = simulation_params['p_fault']
        p_slow = simulation_params['p_slow']
        rho = simulation_params['rho']

        plt.figure(figsize=(8, 6))
        sns.kdeplot(
            ss_acc,
            label='ACC Cars',
            color='dodgerblue',
            shade=True,
            alpha=0.5,
            bw_adjust=0.5,
            clip=(0, None)
        )

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
            f'Stop-Start Frequency Distribution\n(L={L}, N={N}, vmax={vmax}, p_fault={p_fault}, p_slow={p_slow}, rho={rho:.2f})'
        )
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/stop_start_frequency_distribution_density.png", dpi=300)
        plt.close()

    def plot_velocity_cdf(self, velocities_acc, velocities_no_acc, simulation_params):
        L = simulation_params['L']
        N = simulation_params['N']
        vmax = simulation_params['vmax']
        p_fault = simulation_params['p_fault']
        p_slow = simulation_params['p_slow']
        rho = simulation_params['rho']

        plt.figure(figsize=(6,4))
        sorted_acc = np.sort(velocities_acc)
        cdf_acc = np.arange(1, len(sorted_acc) + 1) / len(sorted_acc)

        sorted_no_acc = np.sort(velocities_no_acc)
        cdf_no_acc = np.arange(1, len(sorted_no_acc) + 1) / len(sorted_no_acc)

        bins = range(0, vmax + 3)
        plt.plot(sorted_acc, cdf_acc, label='ACC Cars', color='dodgerblue')
        plt.plot(sorted_no_acc, cdf_no_acc, label='Non-ACC Cars', color='salmon')

        plt.xticks(bins)
        plt.xlim(0, vmax + 2)
        plt.xlabel('Velocity (cells/step)')
        plt.ylabel('Cumulative Probability')
        plt.title(
            f'CDF of Velocities\n(L={L}, N={N}, vmax={vmax}, p_fault={p_fault}, p_slow={p_slow}, rho={rho:.2f})'
        )
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/velocity_cdf.png", dpi=300)
        plt.close()
