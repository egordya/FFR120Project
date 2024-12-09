# MeasurementAndPlotter.py

import matplotlib
import matplotlib.pyplot as plt
from collections import deque
import numpy as np
import multiprocessing
import time
import sys

# Use TkAgg backend for compatibility
matplotlib.use('TkAgg')


def plot_process(queue, N, L):
    """
    Function to run in a separate process for plotting.
    Listens to the queue for incoming data and updates plots.
    """
    # Initialize measurement data
    flow_rate_window = 60  # Number of data points to keep
    flow_rate_road1 = deque(maxlen=flow_rate_window)
    flow_rate_road2 = deque(maxlen=flow_rate_window)
    flow_rate_time = deque(maxlen=flow_rate_window)
    delay_percentage_road1 = deque(maxlen=flow_rate_window)
    delay_percentage_road2 = deque(maxlen=flow_rate_window)
    stopped_cars_road1 = deque(maxlen=flow_rate_window)
    stopped_cars_road2 = deque(maxlen=flow_rate_window)

    # Initialize matplotlib plots
    plt.ion()  # Enable interactive mode
    fig, (ax1, ax3) = plt.subplots(1, 2, figsize=(14, 6))

    # --- Plot 1: Flow Rate and Delay ---
    ax1.set_xlabel('Time (steps)')
    ax1.set_ylabel('Flow Rate (cars/min)', color='tab:red')
    line1_road1, = ax1.plot([], [], 'r-', label='Flow Rate Road 1')
    line1_road2, = ax1.plot([], [], 'r--', label='Flow Rate Road 2')  # Dashed line for Road 2
    ax1.tick_params(axis='y', labelcolor='tab:red')
    ax1.set_ylim(0, 100)  # Adjust based on expected flow rates

    # Secondary y-axis for delay percentage
    ax2 = ax1.twinx()
    ax2.set_ylabel('Average Delay (%)', color='tab:blue')
    line2_road1, = ax2.plot([], [], 'b-', label='Delay Road 1')
    line2_road2, = ax2.plot([], [], 'b--', label='Delay Road 2')  # Dashed line for Road 2
    ax2.tick_params(axis='y', labelcolor='tab:blue')
    ax2.set_ylim(100, 200)  # Adjust based on expected delay percentages

    # Add legends
    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left')

    # --- Plot 2: Bar Chart for Stopped Cars ---
    ax3.set_title('Number of Stopped Cars')
    ax3.set_xlabel('Roads')
    ax3.set_ylabel('Number of Stopped Cars')
    bars = ax3.bar(['Road 1', 'Road 2'], [0, 0], color=['dodgerblue', 'black'])
    ax3.set_ylim(0, N)  # Assuming maximum N stopped cars

    plt.tight_layout()
    plt.show()

    while True:
        try:
            # Wait for new data with a timeout to allow checking for process termination
            data = queue.get(timeout=0.1)
            if data == "TERMINATE":
                print("Plot process received termination signal.")
                break  # Exit the loop to terminate the process

            # Unpack the received data
            step, flow_rate_value_road1, flow_rate_value_road2, delay_road1, delay_road2, stopped_cars_count_road1, stopped_cars_count_road2 = data

            # Update measurement data
            flow_rate_time.append(step)
            flow_rate_road1.append(flow_rate_value_road1)
            flow_rate_road2.append(flow_rate_value_road2)
            delay_percentage_road1.append(delay_road1)
            delay_percentage_road2.append(delay_road2)
            stopped_cars_road1.append(stopped_cars_count_road1)
            stopped_cars_road2.append(stopped_cars_count_road2)

            # Update line plots
            line1_road1.set_xdata(flow_rate_time)
            line1_road1.set_ydata(flow_rate_road1)
            line1_road2.set_xdata(flow_rate_time)
            line1_road2.set_ydata(flow_rate_road2)
            line2_road1.set_xdata(flow_rate_time)
            line2_road1.set_ydata(delay_percentage_road1)
            line2_road2.set_xdata(flow_rate_time)
            line2_road2.set_ydata(delay_percentage_road2)

            # Rescale axes if necessary
            ax1.relim()
            ax1.autoscale_view()
            ax2.relim()
            ax2.autoscale_view()

            # Update bar chart
            if stopped_cars_road1:
                bars[0].set_height(stopped_cars_road1[-1])
            if stopped_cars_road2:
                bars[1].set_height(stopped_cars_road2[-1])

            # Redraw the canvas
            fig.canvas.draw_idle()
            fig.canvas.flush_events()

        except multiprocessing.queues.Empty:
            # No data received, continue the loop
            pass
        except Exception as e:
            print(f"Plot process encountered an error: {e}")
            break  # Exit the loop on unexpected errors

    plt.close(fig)
    sys.exit()


class MeasurementAndPlotter:
    def __init__(self, N, L):
        """
        Initialize measurement tracking and start the plotting process.

        :param N: Number of vehicles per road.
        :param L: Length of the road (number of cells).
        """
        self.N = N
        self.L = L
        self.queue = multiprocessing.Queue()

        # Start the plotting process
        self.plotter_process = multiprocessing.Process(target=plot_process, args=(self.queue, N, L))
        self.plotter_process.start()

    def update_metrics(self, step, flow_rate_value_road1, flow_rate_value_road2,
                       delay_road1, delay_road2, stopped_cars_count_road1, stopped_cars_count_road2):
        """
        Send updated metrics to the plotting process.

        :param step: Current simulation step.
        :param flow_rate_value_road1: Flow rate for Road 1.
        :param flow_rate_value_road2: Flow rate for Road 2.
        :param delay_road1: Average delay for Road 1.
        :param delay_road2: Average delay for Road 2.
        :param stopped_cars_count_road1: Number of stopped cars on Road 1.
        :param stopped_cars_count_road2: Number of stopped cars on Road 2.
        """
        try:
            self.queue.put((step, flow_rate_value_road1, flow_rate_value_road2,
                            delay_road1, delay_road2, stopped_cars_count_road1, stopped_cars_count_road2))
        except Exception as e:
            print(f"Error sending data to plotter: {e}")

    def close_plots(self):
        """
        Send termination signal to the plotting process and wait for it to finish.
        """
        try:
            self.queue.put("TERMINATE")
            self.plotter_process.join()
        except Exception as e:
            print(f"Error terminating plotter process: {e}")
