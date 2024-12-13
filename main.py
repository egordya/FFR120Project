import numpy as np
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

from run_simulation import run_simulation
from HeadLessMeasurementAndPlotter import HeadLessMeasurementAndPlotter


def main():
    # Run simulation in headless mode
    cars_road1, cars_road2, simulation_data = run_simulation(headless=True)

    # Extract parameters
    L = simulation_data['L']
    N = simulation_data['N']
    vmax = simulation_data['vmax']
    p_fault = simulation_data['p_fault']
    p_slow = simulation_data['p_slow']
    rho = simulation_data['rho']

    time_steps = simulation_data['time_steps']
    flow_rate_acc = simulation_data['flow_rate_acc']
    flow_rate_no_acc = simulation_data['flow_rate_no_acc']
    jam_lengths_acc = simulation_data['jam_lengths_acc']
    jam_lengths_no_acc = simulation_data['jam_lengths_no_acc']
    fraction_stopped_road1 = simulation_data['fraction_stopped_road1']
    fraction_stopped_road2 = simulation_data['fraction_stopped_road2']
    delay_acc = simulation_data['delay_acc']
    delay_no_acc = simulation_data['delay_no_acc']
    stop_start_acc = simulation_data['stop_start_acc']
    stop_start_no_acc = simulation_data['stop_start_no_acc']

    # Car-level metrics
    velocities_acc = [car.velocity for car in cars_road1]
    velocities_no_acc = [car.velocity for car in cars_road2]
    stops_acc = [car.stops for car in cars_road1]
    stops_no_acc = [car.stops for car in cars_road2]
    distances_acc = [car.total_distance for car in cars_road1]
    distances_no_acc = [car.total_distance for car in cars_road2]
    speed_offsets_no_acc = [car.speed_offset for car in cars_road2]

    # Calculate percentages of faster and slower drivers
    total_no_acc = len(cars_road2)
    count_faster = sum(1 for offset in speed_offsets_no_acc if offset > 0)
    count_slower = sum(1 for offset in speed_offsets_no_acc if offset < 0)
    percent_faster = (count_faster / total_no_acc) * 100 if total_no_acc > 0 else 0
    percent_slower = (count_slower / total_no_acc) * 100 if total_no_acc > 0 else 0

    # Initialize plotter
    plotter = HeadLessMeasurementAndPlotter(output_dir="plots")

    # Prepare simulation parameters dictionary
    simulation_params = {
        'L': L,
        'N': N,
        'vmax': vmax,
        'p_fault': p_fault,
        'p_slow': p_slow,
        'rho': rho,
    }

    # Existing requested plots with updated velocity and distance traveled distribution
    plotter.plot_velocity_distribution(
        velocities_acc,
        velocities_no_acc,
        simulation_params,
        percent_faster,
        percent_slower
    )
    plotter.plot_distance_traveled_distribution(distances_acc, distances_no_acc, simulation_params)
    plotter.plot_fraction_stopped_over_time(time_steps, fraction_stopped_road1, fraction_stopped_road2,
                                            simulation_params)

    if len(time_steps) == len(flow_rate_acc) == len(flow_rate_no_acc):
        plotter.plot_flow_rate(flow_rate_acc, flow_rate_no_acc, time_steps, simulation_params)

    # Additional metrics
    if jam_lengths_acc and jam_lengths_no_acc and stops_acc and stops_no_acc:
        plotter.plot_additional_metrics(jam_lengths_acc, jam_lengths_no_acc, stops_acc, stops_no_acc, simulation_params)

    # Delay Over Time
    plotter.plot_delay_over_time(time_steps, delay_acc, delay_no_acc, simulation_params)

    # Stop-Start Frequency Distribution
    plotter.plot_stop_start_frequency_distribution(stop_start_acc, stop_start_no_acc, simulation_params)

    # CDF of velocities
    plotter.plot_velocity_cdf(velocities_acc, velocities_no_acc, simulation_params)

    print("All plots generated in 'plots' directory.")


if __name__ == "__main__":
    main()
