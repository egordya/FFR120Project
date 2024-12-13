import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from run_simulation import run_simulation
from HeadLessMeasurementAndPlotter import HeadLessMeasurementAndPlotter


def main():
    # Run simulation in headless mode
    results = run_simulation(density_range=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9], headless=True)

    for rho, flow_rate_acc, flow_rate_no_acc in results:
        # Process each result as needed
        print(f"Density: {rho}")
        print(f"Flow Rate ACC: {flow_rate_acc}")
        print(f"Flow Rate No ACC: {flow_rate_no_acc}")

    # If you need to extract specific data for further processing, you can do so here
    # For example, you might want to analyze or plot specific metrics

    print("All plots generated in 'plots' directory.")


if __name__ == "__main__":
    main()
