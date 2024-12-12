import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for headless plotting
import matplotlib.pyplot as plt

from Car import Car
from MeasurementAndPlotter import MeasurementAndPlotter
from HeadLessMeasurementAndPlotter import HeadLessMeasurementAndPlotter
from run_simulation import run_simulation  # Assume you separated run_simulation into a module

def main():
    # Run the simulation in headless mode
    # Ensure run_simulation returns:
    # cars_road1, cars_road2 = run_simulation(headless=True)
    # Also, you need to gather per-step flow rates and jam lengths inside run_simulation or store them somewhere.
    cars_road1, cars_road2, simulation_data = run_simulation(headless=True)

    # 'simulation_data' is a dictionary (for example) that could include:
    # {
    #   'time_steps': [...],
    #   'flow_rate_acc': [...],
    #   'flow_rate_no_acc': [...],
    #   'jam_lengths_acc': [...],
    #   'jam_lengths_no_acc': [...],
    #   'p_fault': p_fault_used,
    #   'p_slow': p_slow_used,
    # }
    # Adjust based on what you actually log during simulation.

    # Extract data from simulation_data
    time_steps = simulation_data.get('time_steps', [])
    flow_rate_acc = simulation_data.get('flow_rate_acc', [])
    flow_rate_no_acc = simulation_data.get('flow_rate_no_acc', [])
    jam_lengths_acc = simulation_data.get('jam_lengths_acc', [])
    jam_lengths_no_acc = simulation_data.get('jam_lengths_no_acc', [])
    p_fault = simulation_data.get('p_fault', 0.1)
    p_slow = simulation_data.get('p_slow', 0.5)

    # Gather velocities and stops from final car states
    velocities_acc = [car.velocity for car in cars_road1]
    velocities_no_acc = [car.velocity for car in cars_road2]

    stops_acc = [car.stops for car in cars_road1]
    stops_no_acc = [car.stops for car in cars_road2]

    # Example: If you tested different p_fault/p_slow conditions by running multiple simulations
    # and stored their results, you could build a dictionary like this:
    # For now, let's just assume one scenario.
    velocities_no_acc_dict = {
        (p_fault, p_slow): velocities_no_acc
    }

    # Instantiate the headless plotter
    plotter = HeadLessMeasurementAndPlotter(output_dir="plots")

    # 1. Plot the distribution of velocities for ACC and No ACC cars
    plotter.plot_velocity_distribution(velocities_acc, velocities_no_acc)

    # 2. Plot distribution of velocities for different p_fault, p_slow scenarios (if you have multiple)
    # If you only have one scenario, it will just produce one plot.
    plotter.plot_velocity_distribution_with_params(velocities_no_acc_dict, [p_fault], [p_slow])

    # 3. Plot the flow rate for both sets of cars over time
    # Ensure time_steps and flow_rate arrays have the same length
    if len(time_steps) == len(flow_rate_acc) == len(flow_rate_no_acc):
        plotter.plot_flow_rate(flow_rate_acc, flow_rate_no_acc, time_steps)
    else:
        print("Flow rate and time steps array length mismatch. Check your logging.")

    # 4. Additional metrics: jam length, stops distribution, etc.
    if jam_lengths_acc and jam_lengths_no_acc and stops_acc and stops_no_acc:
        plotter.plot_additional_metrics(jam_lengths_acc, jam_lengths_no_acc, stops_acc, stops_no_acc)

    print("All plots generated and saved to the 'plots' directory.")

if __name__ == "__main__":
    main()
