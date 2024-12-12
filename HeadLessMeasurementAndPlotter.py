import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend suitable for headless environments
import matplotlib.pyplot as plt
import numpy as np

class HeadLessMeasurementAndPlotter:
    def __init__(self, output_dir="plots"):
        """
        Initialize the headless measurement and plotter.

        Parameters:
            output_dir (str): Directory to save the plot images.
        """
        self.output_dir = output_dir

    def plot_velocity_distribution(self, velocities_acc, velocities_no_acc):
        """
        Plot the distribution of car velocities for both ACC and Non-ACC cars.

        Parameters:
            velocities_acc (array-like): Velocities of Adaptive Cruise Control Cars.
            velocities_no_acc (array-like): Velocities of Human Driver Cars (No ACC).
        """
        plt.figure(figsize=(6, 4))
        bins = range(0, int(max(np.max(velocities_acc), np.max(velocities_no_acc))) + 2)
        plt.hist(velocities_acc, bins=bins, alpha=0.5, label='Adaptive Cruise Control Cars', color='blue')
        plt.hist(velocities_no_acc, bins=bins, alpha=0.5, label='Human Driver Cars (No ACC)', color='gray')
        plt.xlabel('Velocity (cells/step)')
        plt.ylabel('Number of Cars')
        plt.title('Velocity Distribution')
        plt.legend()
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
            plt.hist(vel_array, bins=bins, alpha=0.7, color='gray')
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
        plt.plot(time_steps, flow_rate_acc, label='Adaptive Cruise Control Cars', color='blue')
        plt.plot(time_steps, flow_rate_no_acc, label='Human Driver Cars (No ACC)', color='gray')
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
        plt.plot(steps, jam_lengths_acc, label='Adaptive Cruise Control Cars', color='blue')
        plt.plot(steps, jam_lengths_no_acc, label='Human Driver Cars (No ACC)', color='gray')
        plt.xlabel('Time (steps)')
        plt.ylabel('Jam Length (cells)')
        plt.title('Jam Length Over Time')
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/jam_length_over_time.png")
        plt.close()

        # Example: Histogram of stops
        plt.figure(figsize=(6,4))
        max_stops = int(max(np.max(stops_acc), np.max(stops_no_acc)))+1
        bins = range(0, max_stops+1)
        plt.hist(stops_acc, bins=bins, alpha=0.5, label='Adaptive Cruise Control Cars', color='blue')
        plt.hist(stops_no_acc, bins=bins, alpha=0.5, label='Human Driver Cars (No ACC)', color='gray')
        plt.xlabel('Number of Stops per Car')
        plt.ylabel('Count of Cars')
        plt.title('Stop Distribution')
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/stops_distribution.png")
        plt.close()

    # Add any other methods for different metrics as needed.

if __name__ == "__main__":
    # Example usage (you must replace these arrays with actual data collected from your simulation)

    # Synthetic data for demonstration
    velocities_acc = np.random.randint(0, 5, size=100)      # 100 ACC cars with random velocities
    velocities_no_acc = np.random.randint(0, 5, size=100)   # 100 Non-ACC cars with random velocities

    # Suppose we tested different p_fault, p_slow combos
    velocities_no_acc_dict = {
        (0.1, 0.5): np.random.randint(0, 5, 100),
        (0.2, 0.5): np.random.randint(0, 5, 100),
    }
    p_fault_values = [0.1, 0.2]
    p_slow_values = [0.5]

    time_steps = np.arange(0, 1000, 10)
    flow_rate_acc = np.random.uniform(0, 10, size=len(time_steps))
    flow_rate_no_acc = np.random.uniform(0, 10, size=len(time_steps))

    jam_lengths_acc = np.random.randint(0, 20, size=len(time_steps))
    jam_lengths_no_acc = np.random.randint(0, 20, size=len(time_steps))
    stops_acc = np.random.randint(0, 10, size=100)
    stops_no_acc = np.random.randint(0, 10, size=100)

    plotter = HeadLessMeasurementAndPlotter()

    # Plot velocities
    plotter.plot_velocity_distribution(velocities_acc, velocities_no_acc)
    plotter.plot_velocity_distribution_with_params(velocities_no_acc_dict, p_fault_values, p_slow_values)

    # Plot flow rate
    plotter.plot_flow_rate(flow_rate_acc, flow_rate_no_acc, time_steps)

    # Additional metrics
    plotter.plot_additional_metrics(jam_lengths_acc, jam_lengths_no_acc, stops_acc, stops_no_acc)

    print("Plots generated and saved to 'plots' directory.")
