# run_simulation.py

import sys
import numpy as np
import matplotlib

matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt

from Car import Car
from MeasurementAndPlotter import MeasurementAndPlotter


def run_simulation(density_range, headless=False):
    # Simulation Parameters
    L = 120  # Road length
    vmax = 4  # Maximum speed
    p_fault = 0.1  # Probability of random slowdown
    p_slow = 0.5  # Probability of slow-to-start behavior
    steps = 5000  # Number of steps

    prob_faster = 0.40
    prob_slower = 0.10
    prob_normal = 0.50

    # Validate that probabilities sum to 1
    if not np.isclose(prob_faster + prob_slower + prob_normal, 1.0):
        raise ValueError("prob_faster, prob_slower, and prob_normal must sum to 1.")

    results = []

    for rho in density_range:
        N = int(rho * L)  # Calculate number of cars based on density
        cruise_control_percentage_road1 = 100
        N_ACC_CARS = int(cruise_control_percentage_road1 / 100 * N)

        # Initialize simulation_data with new arrays
        simulation_data = {
            'time_steps': [],
            'flow_rate_acc': [],
            'flow_rate_no_acc': [],
            # ... other metrics ...
        }

        # Initialize Roads
        cars_road1 = initialize_cars(N, L, vmax, p_fault, p_slow, prob_faster, prob_slower, prob_normal, True)
        cars_road2 = initialize_cars(N, L, vmax, p_fault, p_slow, prob_faster, prob_slower, prob_normal, False)

        # Run the simulation
        for step in range(steps):
            update_road(cars_road1, L)
            update_road(cars_road2, L)

            # Compute metrics
            average_speed_road1 = np.mean([c.velocity for c in cars_road1])
            average_speed_road2 = np.mean([c.velocity for c in cars_road2])

            simulation_data['time_steps'].append(step)
            simulation_data['flow_rate_acc'].append(average_speed_road1)
            simulation_data['flow_rate_no_acc'].append(average_speed_road2)

        # Store results for this density
        results.append((rho, simulation_data['flow_rate_acc'], simulation_data['flow_rate_no_acc']))

    # Plot the results
    plot_flow_rate_sweep(results)

    return results


def plot_flow_rate_sweep(results):
    plt.figure(figsize=(10, 6))
    for rho, flow_rate_acc, flow_rate_no_acc in results:
        plt.plot(flow_rate_acc, label=f'ACC Cars (Density: {rho:.2f})', linestyle='-')
        plt.plot(flow_rate_no_acc, label=f'Non-ACC Cars (Density: {rho:.2f})', linestyle='--')

    plt.xlabel('Time (steps)')
    plt.ylabel('Flow Rate (cars/step)')
    plt.title('Flow Rate Over Time for Different Densities')
    plt.legend()
    plt.tight_layout()
    plt.savefig('plots/flow_rate_sweep.png')
    plt.close()


def initialize_cars(N, L, vmax, p_fault, p_slow, prob_faster, prob_slower, prob_normal, acc_enabled):
    cars = []
    occupied_positions = set()
    for _ in range(N):
        position = np.random.randint(0, L)
        while position in occupied_positions:
            position = np.random.randint(0, L)
        occupied_positions.add(position)
        car = Car(
            road_length=L,
            cell_width=1,
            max_speed=vmax,
            p_fault=p_fault,
            p_slow=p_slow,
            prob_faster=prob_faster,
            prob_slower=prob_slower,
            prob_normal=prob_normal,
            position=position,
            adaptive_cruise_control=acc_enabled
        )
        cars.append(car)
    return cars


def update_road(cars, L):
    cars_sorted = sorted(cars, key=lambda c: c.position)
    for i, car in enumerate(cars_sorted):
        if i < len(cars_sorted) - 1:
            next_car = cars_sorted[i + 1]
            distance = next_car.position - car.position - 1
            if distance < 0:
                distance += L
        else:
            next_car = cars_sorted[0]
            distance = (next_car.position + L) - car.position - 1
        velocity_of_next_car = next_car.velocity
        car.update_velocity(distance, velocity_of_next_car)

    for car in cars_sorted:
        car.move()


if __name__ == "__main__":
    run_simulation(density_range=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0], headless=False)
