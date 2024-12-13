# plot_3d_flowrate_acc_nonacc_combined.py

import numpy as np
import plotly.graph_objects as go
from run_simulation import run_simulation


def mean_flow_rate_vs_rho_pfault_plot_combined(
    L=120,
    vmax=4,
    p_slow=0.5,
    steps=1000,
    prob_faster=0.1,
    prob_slower=0.2,
    prob_normal=0.7
):
    """
    Generates a combined 3D surface plot for both ACC and Non-ACC Cars showing mean flow rate
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
    rho_values = np.linspace(0.0, 1.0, 21)  # 21 points from 0.0 to 1.0 inclusive
    p_fault_values = np.linspace(0, 1.0, 11)  # 11 points from 0 to 1.0

    # Prepare storage for results
    mean_flow_rate_matrix_non_acc = np.zeros((len(rho_values), len(p_fault_values)))
    mean_flow_rate_matrix_acc = np.zeros((len(rho_values), len(p_fault_values)))

    # Sweep over rho and p_fault for Non-ACC Cars
    for i, rho in enumerate(rho_values):
        N = int(rho * (L / 2))  # Convert rho to number of cars
        if N == 0:
            # If rho is 0, no cars are present; flow rate remains 0
            mean_flow_rate_matrix_non_acc[i, :] = 0
            print(f"Non-ACC Simulation {i + 1}/{len(rho_values)} for rho={rho:.2f}, p_fault=All Zero (No Cars)")
        else:
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

                # Compute mean flow rate for Non-ACC cars (Road 2)
                mean_flow_rate_non_acc = (
                    np.mean(simulation_data['flow_rate_no_acc'])
                    if simulation_data['flow_rate_no_acc']
                    else 0
                )
                mean_flow_rate_matrix_non_acc[i, j] = mean_flow_rate_non_acc

    # Sweep over rho and p_fault for ACC Cars
    for i, rho in enumerate(rho_values):
        N = int(rho * (L / 2))  # Convert rho to number of cars
        if N == 0:
            # If rho is 0, no cars are present; flow rate remains 0
            mean_flow_rate_matrix_acc[i, :] = 0
            print(f"ACC Simulation {i + 1}/{len(rho_values)} for rho={rho:.2f}, p_fault=All Zero (No Cars)")
        else:
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

                # Compute mean flow rate for ACC cars (Road 1)
                mean_flow_rate_acc = (
                    np.mean(simulation_data['flow_rate_acc'])
                    if simulation_data['flow_rate_acc']
                    else 0
                )
                mean_flow_rate_matrix_acc[i, j] = mean_flow_rate_acc

    # Create a combined 3D surface plot using Plotly
    fig_combined = go.Figure()

    # Add Non-ACC Cars surface
    fig_combined.add_trace(go.Surface(
        x=p_fault_values,            # x-axis: p_fault
        y=rho_values,                # y-axis: rho (density)
        z=mean_flow_rate_matrix_non_acc,  # z-axis: mean flow rate for Non-ACC cars
        colorscale='Viridis',
        name='Non-ACC Cars',
        showscale=False,
        opacity=0.8
    ))

    # Add ACC Cars surface
    fig_combined.add_trace(go.Surface(
        x=p_fault_values,            # x-axis: p_fault
        y=rho_values,                # y-axis: rho (density)
        z=mean_flow_rate_matrix_acc, # z-axis: mean flow rate for ACC cars
        colorscale='Cividis',
        name='ACC Cars',
        showscale=False,
        opacity=0.8
    ))

    # Add annotations manually to indicate which surface is which
    fig_combined.add_trace(go.Scatter3d(
        x=[None], y=[None], z=[None],
        mode='markers',
        marker=dict(
            size=10,
            color='Viridis',
            showscale=False
        ),
        name='Non-ACC Cars'
    ))

    fig_combined.add_trace(go.Scatter3d(
        x=[None], y=[None], z=[None],
        mode='markers',
        marker=dict(
            size=10,
            color='Cividis',
            showscale=False
        ),
        name='ACC Cars'
    ))

    # Update layout with titles including vmax=4
    fig_combined.update_layout(
        title="Mean Flow Rate (ACC & Non-ACC Cars, vmax=4) vs Density (ρ) and p_fault",
        scene=dict(
            xaxis_title='p_fault (Probability of Random Slowdown)',
            yaxis_title='ρ (Traffic Density)',
            zaxis_title='Mean Flow Rate (cars/step)'
        ),
        autosize=False,
        width=1000,
        height=800,
        margin=dict(l=65, r=50, b=65, t=90),
        legend=dict(
            x=0.7,
            y=0.95,
            bgcolor='rgba(255,255,255,0)',
            bordercolor='rgba(0,0,0,0)'
        )
    )

    # Workaround to add a legend by adding dummy traces
    fig_combined.add_trace(go.Scatter3d(
        x=[None], y=[None], z=[None],
        mode='markers',
        marker=dict(
            size=10,
            color='Viridis',
            showscale=False
        ),
        name='Non-ACC Cars'
    ))

    fig_combined.add_trace(go.Scatter3d(
        x=[None], y=[None], z=[None],
        mode='markers',
        marker=dict(
            size=10,
            color='Cividis',
            showscale=False
        ),
        name='ACC Cars'
    ))

    # Save the combined plot as an HTML file
    fig_combined.write_html("mean_flow_rate_vs_rho_pfault_combined.html")
    print("Combined 3D Plot for ACC and Non-ACC Cars saved as 'mean_flow_rate_vs_rho_pfault_combined.html'.")


if __name__ == "__main__":
    mean_flow_rate_vs_rho_pfault_plot_combined()
