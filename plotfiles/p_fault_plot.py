import numpy as np
import plotly.graph_objects as go
from run_simulation import run_simulation


def p_fault_plot():
    # Parameters for the sweep
    L = 120  # Road length
    vmax = 4  # Max speed
    p_slow = 0.5  # Keep p_slow fixed for now
    steps = 1  # Fewer steps for quicker runs, adjust as needed
    prob_faster = 0.1
    prob_slower = 0.2
    prob_normal = 0.7

    # Sweep over N (to vary density) and p_fault
    N_values = np.arange(0, int(L / 2) + 1, 10)  # Every 10 cars
    p_fault_values = np.linspace(0, 0.5, 6)  # 6 values from 0 to 0.5

    # Prepare storage for results
    # We'll store average flow rates for ACC cars in a 2D array
    flow_rate_acc_matrix = np.zeros((len(N_values), len(p_fault_values)))
    flow_rate_no_acc_matrix = np.zeros((len(N_values), len(p_fault_values)))
    rho_values = np.zeros((len(N_values), len(p_fault_values)))

    # Run the simulations
    for i, N in enumerate(N_values):
        for j, p_fault in enumerate(p_fault_values):
            # Run simulation headless with given parameters
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

            # Extract data
            flow_rate_acc = simulation_data['flow_rate_acc']
            flow_rate_no_acc = simulation_data['flow_rate_no_acc']
            rho = simulation_data['rho']  # This should be N/(L/2)

            # Compute mean flow rates over the simulation period
            mean_flow_rate_acc = np.mean(flow_rate_acc) if flow_rate_acc else 0
            mean_flow_rate_no_acc = np.mean(flow_rate_no_acc) if flow_rate_no_acc else 0

            flow_rate_acc_matrix[i, j] = mean_flow_rate_acc
            flow_rate_no_acc_matrix[i, j] = mean_flow_rate_no_acc
            rho_values[i, j] = rho

    # Create a 3D surface plot of flow rate_acc vs. rho vs. p_fault using Plotly
    fig = go.Figure(data=[go.Surface(
        x=p_fault_values,  # x-axis: p_fault
        y=N_values,  # y-axis: N (related to rho)
        z=flow_rate_acc_matrix  # z-axis: mean flow rate for ACC
    )])

    fig.update_layout(
        title="Mean Flow Rate (ACC Cars) as a Function of Density (via N) and p_fault",
        scene=dict(
            xaxis_title='p_fault',
            yaxis_title='N (Number of Cars)',
            zaxis_title='Mean Flow Rate (ACC)'
        ),
        autosize=False,
        width=700,
        height=600,
        margin=dict(l=65, r=50, b=65, t=90)
    )

    # Save the figure as HTML
    fig.write_html("flow_rate_3d_surface.html")
    print("3D Plot saved as 'flow_rate_3d_surface.html'.")


if __name__ == "__main__":
    p_fault_plot()
