# plot_3d_acc_nonacc.py

import numpy as np
import plotly.graph_objects as go
from run_simulation import run_simulation


def mean_velocity_vs_rho_pfault_plot_non_acc(L=120, vmax=4, p_slow=0.5, steps=1000,
                                             prob_faster=0.1, prob_slower=0.2, prob_normal=0.7):
    """
    Generates a 3D surface plot for Non-ACC Cars (Road 2) showing mean velocity
    as a function of traffic density (rho) and probability of random slowdown (p_fault).

    Parameters:
        L (int): Road length.
        vmax (int): Maximum speed of cars.
        p_slow (float): Probability of slow-to-start behavior.
        steps (int): Number of simulation steps.
        prob_faster (float): Probability of faster drivers.
        prob_slower (float): Probability of slower drivers.
        prob_normal (float): Probability of normal drivers.
    """
    # Define ranges for rho and p_fault
    rho_values = np.linspace(0.05, 1.0, 20)  # 20 points from 0.05 to 1.0 to avoid N=0
    p_fault_values = np.linspace(0, 1.0, 11)  # 11 points from 0 to 0.5

    # Prepare storage for results
    mean_velocity_matrix_non_acc = np.zeros((len(rho_values), len(p_fault_values)))

    # Sweep over rho and p_fault
    for i, rho in enumerate(rho_values):
        N = int(rho * (L / 2))  # Convert rho to number of cars
        if N == 0:
            N = 1  # Ensure at least one car for simulation
        for j, p_fault in enumerate(p_fault_values):
            print(f"Non-ACC Simulation {i + 1}/{len(rho_values)} for rho={rho:.2f}, p_fault={p_fault:.2f}")
            # Run the simulation
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

            # Compute mean velocity for Non-ACC cars (Road 2)
            mean_velocity_non_acc = np.mean([car.velocity for car in cars_road2]) if cars_road2 else 0
            mean_velocity_matrix_non_acc[i, j] = mean_velocity_non_acc

    # Create a 3D surface plot using Plotly for Non-ACC Cars
    fig_non_acc = go.Figure(data=[go.Surface(
        x=p_fault_values,  # x-axis: p_fault
        y=rho_values,  # y-axis: rho (density)
        z=mean_velocity_matrix_non_acc,  # z-axis: mean velocity for Non-ACC cars
        colorscale='Viridis',
        name='Non-ACC Cars'
    )])

    fig_non_acc.update_layout(
        title="Mean Velocity (Non-ACC Cars) vs Density (ρ) and p_fault with Max Velocity 4",
        scene=dict(
            xaxis_title='p_fault (Probability of Random Slowdown)',
            yaxis_title='ρ (Traffic Density)',
            zaxis_title='Mean Velocity (cells/step)'
        ),
        autosize=False,
        width=800,
        height=700,
        margin=dict(l=65, r=50, b=65, t=90)
    )

    # Save the Non-ACC plot as an HTML file
    fig_non_acc.write_html("mean_velocity_vs_rho_pfault_non_acc.html")
    # Save the Non-ACC plot as a high-resolution PNG
    fig_non_acc.write_image("mean_velocity_vs_rho_pfault_non_acc.png", width=1920, height=1080, scale=2)
    print("3D Plot for Non-ACC Cars saved as 'mean_velocity_vs_rho_pfault_non_acc.png'.")


    print("3D Plot for Non-ACC Cars saved as 'mean_velocity_vs_rho_pfault_non_acc.html'.")


def mean_velocity_vs_rho_pfault_plot_acc(L=120, vmax=4, p_slow=0.5, steps=1000,
                                         prob_faster=0.1, prob_slower=0.2, prob_normal=0.7):
    """
    Generates a 3D surface plot for ACC Cars (Road 1) showing mean velocity
    as a function of traffic density (rho) and probability of random slowdown (p_fault).

    Parameters:
        L (int): Road length.
        vmax (int): Maximum speed of cars.
        p_slow (float): Probability of slow-to-start behavior.
        steps (int): Number of simulation steps.
        prob_faster (float): Probability of faster drivers.
        prob_slower (float): Probability of slower drivers.
        prob_normal (float): Probability of normal drivers.
    """
    # Define ranges for rho and p_fault
    rho_values = np.linspace(0.05, 1.0, 20)  # 20 points from 0.05 to 1.0 to avoid N=0
    p_fault_values = np.linspace(0, 1.0, 11)  # 11 points from 0 to 0.5

    # Prepare storage for results
    mean_velocity_matrix_acc = np.zeros((len(rho_values), len(p_fault_values)))

    # Sweep over rho and p_fault
    for i, rho in enumerate(rho_values):
        N = int(rho * (L / 2))  # Convert rho to number of cars
        if N == 0:
            N = 1  # Ensure at least one car for simulation
        for j, p_fault in enumerate(p_fault_values):
            print(f"ACC Simulation {i + 1}/{len(rho_values)} for rho={rho:.2f}, p_fault={p_fault:.2f}")
            # Run the simulation
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

            # Compute mean velocity for ACC cars (Road 1)
            mean_velocity_acc = np.mean([car.velocity for car in cars_road1]) if cars_road1 else 0
            mean_velocity_matrix_acc[i, j] = mean_velocity_acc

    # Create a 3D surface plot using Plotly for ACC Cars
    fig_acc = go.Figure(data=[go.Surface(
        x=p_fault_values,  # x-axis: p_fault
        y=rho_values,  # y-axis: rho (density)
        z=mean_velocity_matrix_acc,  # z-axis: mean velocity for ACC cars
        colorscale='Cividis',
        name='ACC Cars'
    )])

    fig_acc.update_layout(
        title="Mean Velocity (ACC Cars) vs Density (ρ) and p_fault with Max Velocity 4",
        scene=dict(
            xaxis_title='p_fault (Probability of Random Slowdown)',
            yaxis_title='ρ (Traffic Density)',
            zaxis_title='Mean Velocity (cells/step)'
        ),
        autosize=False,
        width=800,
        height=700,
        margin=dict(l=65, r=50, b=65, t=90)
    )

    # Save the ACC plot as an HTML file
    fig_acc.write_html("mean_velocity_vs_rho_pfault_acc.html")
    # Save the ACC plot as a high-resolution PNG
    fig_acc.write_image("mean_velocity_vs_rho_pfault_acc.png", width=1920, height=1080, scale=2)
    print("3D Plot for ACC Cars saved as 'mean_velocity_vs_rho_pfault_acc.png'.")

    print("3D Plot for ACC Cars saved as 'mean_velocity_vs_rho_pfault_acc.html'.")


if __name__ == "__main__":
    mean_velocity_vs_rho_pfault_plot_non_acc()
    mean_velocity_vs_rho_pfault_plot_acc()
