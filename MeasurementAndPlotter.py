# MeasurementAndPlotter.py


import os
import seaborn as sns
import matplotlib.pyplot as plt
from collections import deque
import multiprocessing
import sys
import queue
import matplotlib

matplotlib.use('TkAgg')

COLOR_RED = "#E53D00"
COLOR_YELLOW = "#FFE900"
COLOR_TEAL = "#21A0A0"
COLOR_DARKTEAL = "#046865"
# COLOR_DARKGREY = "#A9A9A9"  # Removed old dark grey
COLOR_WHITE = "#FCFFF7"
COLOR_GREEN = "#1d821d"  # New green color
COLOR_ORANGE = "#de9c18"

sns.set_style("darkgrid")

def flow_delay_plot_process(data_queue, control_queue, N, L, vmax):
    plt.ion()

    # Flow and Delay Figure
    fig_flow, ax1 = plt.subplots(figsize=(10, 6))
    ax1.set_xlabel('Time (steps)')
    ax1.set_ylabel('Flow Rate (cars/min)', color=COLOR_RED)
    line_flow_acc, = ax1.plot([], [], color=COLOR_RED, linestyle='-', label='Flow Rate Adaptive Cruise Control Cars')
    line_flow_no_acc, = ax1.plot([], [], color=COLOR_RED, linestyle='--', label='Flow Rate Human Driver Cars (No ACC)')
    ax1.tick_params(axis='y', labelcolor=COLOR_RED)
    ax1.set_ylim(0, vmax * 1.2)  # Now 'vmax' is defined

    ax2 = ax1.twinx()
    ax2.set_ylabel('Average Delay (%)', color=COLOR_TEAL)
    line_delay_acc, = ax2.plot([], [], color=COLOR_TEAL, linestyle='-', label='Delay Adaptive Cruise Control Cars')
    line_delay_no_acc, = ax2.plot([], [], color=COLOR_TEAL, linestyle='--', label='Delay Human Driver Cars (No ACC)')
    ax2.tick_params(axis='y', labelcolor=COLOR_TEAL)
    ax2.set_ylim(0, 300)  # Adjust as needed

    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left')
    plt.tight_layout()

    flow_rate_window = 60
    flow_rate_acc = deque(maxlen=flow_rate_window)
    flow_rate_no_acc = deque(maxlen=flow_rate_window)
    flow_rate_time = deque(maxlen=flow_rate_window)
    delay_acc = deque(maxlen=flow_rate_window)
    delay_no_acc = deque(maxlen=flow_rate_window)

    def on_key_press_flow(event):
        if event.key == 'escape':
            print("ESC pressed in flow/delay plot window. Sending termination signal.")
            control_queue.put("TERMINATE_FROM_PLOT")
            plt.close(fig_flow)

    fig_flow.canvas.mpl_connect('key_press_event', on_key_press_flow)

    plt.show()

    while True:
        try:
            data = data_queue.get(timeout=0.1)
            if data == "TERMINATE":
                print("Flow/Delay plot process received termination signal.")
                break

            step, fr1, fr2, d1, d2, sc1, sc2 = data
            flow_rate_time.append(step)
            flow_rate_acc.append(fr1)
            flow_rate_no_acc.append(fr2)
            delay_acc.append(d1)
            delay_no_acc.append(d2)

            # Update lines
            line_flow_acc.set_data(flow_rate_time, flow_rate_acc)
            line_flow_no_acc.set_data(flow_rate_time, flow_rate_no_acc)
            line_delay_acc.set_data(flow_rate_time, delay_acc)
            line_delay_no_acc.set_data(flow_rate_time, delay_no_acc)

            ax1.relim()
            ax1.autoscale_view()
            ax2.relim()
            ax2.autoscale_view()



            fig_flow.canvas.draw_idle()
            fig_flow.canvas.flush_events()
            plt.pause(0.001)

        except queue.Empty:
            pass
        except Exception as e:
            print(f"Flow/Delay plot process encountered an error: {e}")
            break

    plt.close(fig_flow)
    sys.exit()


def cars_stopped_plot_process(data_queue, control_queue, N, L):
    plt.ion()

    # Number of Stopped Cars Figure
    fig_stopped, ax_stopped = plt.subplots(figsize=(6, 6))
    ax_stopped.set_title('Number of Stopped Cars')
    ax_stopped.set_xlabel('Roads')
    ax_stopped.set_ylabel('Number of Stopped Cars')
    bars = ax_stopped.bar(['Adaptive Cruise Control Cars', 'Human Driver Cars (No ACC)'], [0, 0],
                          color=[COLOR_TEAL, COLOR_GREEN])
    ax_stopped.set_ylim(0, N)
    plt.tight_layout()

    def on_key_press_stopped(event):
        if event.key == 'escape':
            print("ESC pressed in stopped cars plot window. Sending termination signal.")
            control_queue.put("TERMINATE_FROM_PLOT")
            plt.close(fig_stopped)

    fig_stopped.canvas.mpl_connect('key_press_event', on_key_press_stopped)

    plt.show()

    while True:
        try:
            data = data_queue.get(timeout=0.1)
            if data == "TERMINATE":
                print("Cars Stopped plot process received termination signal.")
                break

            step, fr1, fr2, d1, d2, sc1, sc2 = data
            # Update bars
            bars[0].set_height(sc1)
            bars[1].set_height(sc2)

            ax_stopped.set_ylim(0, max(N, sc1, sc2) + 5)

            fig_stopped.canvas.draw_idle()
            fig_stopped.canvas.flush_events()
            plt.pause(0.001)

        except queue.Empty:
            pass
        except Exception as e:
            print(f"Cars Stopped plot process encountered an error: {e}")
            break

    plt.close(fig_stopped)
    sys.exit()

def density_occupancy_plot_process(data_queue, control_queue):
    plt.ion()
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_title("Density and Occupancy Over Time")
    ax.set_xlabel("Time (steps)")
    ax.set_ylabel("Density (veh/cell)", color=COLOR_RED)
    line_density_r1, = ax.plot([], [], color=COLOR_RED, linestyle='-', label='Density Adaptive Cruise Control Cars')
    line_density_r2, = ax.plot([], [], color=COLOR_GREEN, linestyle='--', label='Density Human Driver Cars (No ACC)')
    ax.set_ylim(0, 1)
    ax.tick_params(axis='y', labelcolor=COLOR_RED)

    ax2 = ax.twinx()
    ax2.set_ylabel("Occupancy (%)", color=COLOR_TEAL)
    line_occupancy_r1, = ax2.plot([], [], color=COLOR_TEAL, linestyle='-', label='Occupancy Adaptive Cruise Control Cars')
    line_occupancy_r2, = ax2.plot([], [], color=COLOR_GREEN, linestyle='--', label='Occupancy Human Driver Cars (No ACC)')
    ax2.set_ylim(0, 100)
    ax2.tick_params(axis='y', labelcolor=COLOR_TEAL)

    lines_1, labels_1 = ax.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left')
    plt.tight_layout()

    time_data = deque(maxlen=300)
    density_data_r1 = deque(maxlen=300)
    density_data_r2 = deque(maxlen=300)
    occupancy_data_r1 = deque(maxlen=300)
    occupancy_data_r2 = deque(maxlen=300)

    def on_key_press(event):
        if event.key == 'escape':
            print("ESC pressed in density/occupancy plot window. Sending termination signal.")
            control_queue.put("TERMINATE_FROM_PLOT")
            plt.close(fig)

    fig.canvas.mpl_connect('key_press_event', on_key_press)

    plt.show()

    while True:
        try:
            data = data_queue.get(timeout=0.1)
            if data == "TERMINATE":
                print("Density/Occupancy plot process received termination signal.")
                break

            step, density_r1, occupancy_r1_val, density_r2, occupancy_r2_val = data
            time_data.append(step)
            density_data_r1.append(density_r1)
            occupancy_data_r1.append(occupancy_r1_val)
            density_data_r2.append(density_r2)
            occupancy_data_r2.append(occupancy_r2_val)

            # Update lines
            line_density_r1.set_data(time_data, density_data_r1)
            line_density_r2.set_data(time_data, density_data_r2)
            line_occupancy_r1.set_data(time_data, occupancy_data_r1)
            line_occupancy_r2.set_data(time_data, occupancy_data_r2)

            ax.relim()
            ax.autoscale_view()
            ax2.relim()
            ax2.autoscale_view()

            fig.canvas.draw_idle()
            fig.canvas.flush_events()
            plt.pause(0.001)

        except queue.Empty:
            pass
        except Exception as e:
            print(f"Density/Occupancy plot process encountered an error: {e}")
            break

    plt.close(fig)
    sys.exit()

def jam_queue_plot_process(data_queue, control_queue):
    plt.ion()
    fig, ax = plt.subplots(figsize=(10,5))
    ax.set_title("Jam Length and Queue Duration Over Time")
    ax.set_xlabel("Time (steps)")
    ax.set_ylabel("Jam Length (cells)", color=COLOR_RED)
    line_jam_r1, = ax.plot([], [], color=COLOR_RED, linestyle='-', label='Jam Length Road 1')
    line_jam_r2, = ax.plot([], [], color=COLOR_GREEN, linestyle='--', label='Jam Length Road 2')
    ax.set_ylim(0, 50)
    ax.tick_params(axis='y', labelcolor=COLOR_RED)

    ax2 = ax.twinx()
    ax2.set_ylabel("Queue Duration (steps)", color=COLOR_TEAL)
    line_queue_r1, = ax2.plot([], [], color=COLOR_TEAL, linestyle='-', label='Queue Duration Road 1')
    line_queue_r2, = ax2.plot([], [], color=COLOR_GREEN, linestyle='--', label='Queue Duration Road 2')
    ax2.set_ylim(0, 300)
    ax2.tick_params(axis='y', labelcolor=COLOR_TEAL)

    lines_1, labels_1 = ax.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left')
    plt.tight_layout()

    time_data = deque(maxlen=300)
    jam_length_r1 = deque(maxlen=300)
    jam_length_r2 = deque(maxlen=300)
    queue_duration_r1 = deque(maxlen=300)
    queue_duration_r2 = deque(maxlen=300)

    def on_key_press(event):
        if event.key == 'escape':
            print("ESC pressed in jam/queue plot window. Sending termination signal.")
            control_queue.put("TERMINATE_FROM_PLOT")
            plt.close(fig)

    fig.canvas.mpl_connect('key_press_event', on_key_press)

    plt.show()

    while True:
        try:
            data = data_queue.get(timeout=0.1)
            if data == "TERMINATE":
                print("Jam/Queue plot process received termination signal.")
                break

            step, jl_r1, jl_r2, qd_r1, qd_r2 = data
            time_data.append(step)
            jam_length_r1.append(jl_r1)
            jam_length_r2.append(jl_r2)
            queue_duration_r1.append(qd_r1)
            queue_duration_r2.append(qd_r2)

            # Update lines
            line_jam_r1.set_data(time_data, jam_length_r1)
            line_jam_r2.set_data(time_data, jam_length_r2)
            line_queue_r1.set_data(time_data, queue_duration_r1)
            line_queue_r2.set_data(time_data, queue_duration_r2)

            ax.relim()
            ax.autoscale_view()
            ax2.relim()
            ax2.autoscale_view()

            fig.canvas.draw_idle()
            fig.canvas.flush_events()
            plt.pause(0.001)

        except queue.Empty:
            pass
        except Exception as e:
            print(f"Jam/Queue plot process encountered an error: {e}")
            break

    plt.close(fig)
    sys.exit()


class MeasurementAndPlotter:
    def __init__(self, N, L, vmax,
                 enable_flow_delay_plot=True,
                 enable_cars_stopped_plot=True,
                 enable_density_occupancy_plot=True,
                 enable_jam_queue_plot=True,
                 enable_fuel_consumption_plot=True):
        self.N = N
        self.L = L
        self.vmax = vmax  # Store vmax for passing to plotting processes
        self.enable_flow_delay_plot = enable_flow_delay_plot
        self.enable_cars_stopped_plot = enable_cars_stopped_plot
        self.enable_density_occupancy_plot = enable_density_occupancy_plot
        self.enable_jam_queue_plot = enable_jam_queue_plot
        self.enable_fuel_consumption_plot = enable_fuel_consumption_plot

        self.data_queue_flow_delay = None
        self.control_queue_flow_delay = None
        self.plotter_process_flow_delay = None

        self.data_queue_cars_stopped = None
        self.control_queue_cars_stopped = None
        self.plotter_process_cars_stopped = None

        self.density_occupancy_queue = None
        self.density_occupancy_control_queue = None
        self.density_occupancy_process = None

        self.jam_queue_queue = None
        self.jam_queue_control_queue = None
        self.jam_queue_process = None

        # Flow and Delay Plot
        if self.enable_flow_delay_plot:
            self.data_queue_flow_delay = multiprocessing.Queue()
            self.control_queue_flow_delay = multiprocessing.Queue()
            self.plotter_process_flow_delay = multiprocessing.Process(
                target=flow_delay_plot_process,
                args=(self.data_queue_flow_delay, self.control_queue_flow_delay, self.N, self.L, self.vmax)
            )
            self.plotter_process_flow_delay.start()

        # Cars Stopped Plot
        if self.enable_cars_stopped_plot:
            self.data_queue_cars_stopped = multiprocessing.Queue()
            self.control_queue_cars_stopped = multiprocessing.Queue()
            self.plotter_process_cars_stopped = multiprocessing.Process(
                target=cars_stopped_plot_process,
                args=(self.data_queue_cars_stopped, self.control_queue_cars_stopped, self.N, self.L)
            )
            self.plotter_process_cars_stopped.start()

        # Density/Occupancy Plot
        if self.enable_density_occupancy_plot:
            self.density_occupancy_queue = multiprocessing.Queue()
            self.density_occupancy_control_queue = multiprocessing.Queue()
            self.density_occupancy_process = multiprocessing.Process(
                target=density_occupancy_plot_process,
                args=(self.density_occupancy_queue, self.density_occupancy_control_queue)
            )
            self.density_occupancy_process.start()

        # Jam/Queue Plot
        if self.enable_jam_queue_plot:
            self.jam_queue_queue = multiprocessing.Queue()
            self.jam_queue_control_queue = multiprocessing.Queue()
            self.jam_queue_process = multiprocessing.Process(
                target=jam_queue_plot_process,
                args=(self.jam_queue_queue, self.jam_queue_control_queue)
            )
            self.jam_queue_process.start()

    def update_flow_delay_metrics(self, step, flow_acc, flow_no_acc, delay_acc, delay_no_acc):
        if self.enable_flow_delay_plot:
            try:
                self.data_queue_flow_delay.put((step, flow_acc, flow_no_acc, delay_acc, delay_no_acc, 0, 0))
            except Exception as e:
                print(f"Error sending data to flow/delay plotter: {e}")

    def update_cars_stopped_metrics(self, step, stopped_acc, stopped_no_acc):
        if self.enable_cars_stopped_plot:
            try:
                # The flow_delay_plot_process expects (step, fr1, fr2, d1, d2, sc1, sc2)
                # Since we are updating cars stopped separately, we'll pass dummy values for other metrics
                self.data_queue_cars_stopped.put((step, 0, 0, 0, 0, stopped_acc, stopped_no_acc))
            except Exception as e:
                print(f"Error sending data to cars stopped plotter: {e}")

    def update_density_occupancy(self, step, density_r1, occupancy_r1, density_r2, occupancy_r2):
        if self.enable_density_occupancy_plot:
            try:
                self.density_occupancy_queue.put((step, density_r1, occupancy_r1, density_r2, occupancy_r2))
            except Exception as e:
                print(f"Error sending density/occupancy data: {e}")

    def update_jam_queue_metrics(self, step, jam_length_r1, jam_length_r2, queue_duration_r1, queue_duration_r2):
        if self.enable_jam_queue_plot:
            try:
                self.jam_queue_queue.put((step, jam_length_r1, jam_length_r2, queue_duration_r1, queue_duration_r2))
            except Exception as e:
                print(f"Error sending jam/queue data: {e}")

    def check_control_messages(self):
        # Check flow/delay plot
        if self.enable_flow_delay_plot:
            try:
                message = self.control_queue_flow_delay.get_nowait()
                return message
            except queue.Empty:
                pass
            except Exception as e:
                print(f"Error reading control messages from flow/delay plot: {e}")

        # Check cars stopped plot
        if self.enable_cars_stopped_plot:
            try:
                message = self.control_queue_cars_stopped.get_nowait()
                return message
            except queue.Empty:
                pass
            except Exception as e:
                print(f"Error reading control messages from cars stopped plot: {e}")

        # Check density/occupancy plot
        if self.enable_density_occupancy_plot:
            try:
                message = self.density_occupancy_control_queue.get_nowait()
                return message
            except queue.Empty:
                pass
            except Exception as e:
                print(f"Error reading density/occupancy control messages: {e}")

        # Check jam/queue plot
        if self.enable_jam_queue_plot:
            try:
                message = self.jam_queue_control_queue.get_nowait()
                return message
            except queue.Empty:
                pass
            except Exception as e:
                print(f"Error reading jam/queue control messages: {e}")

        return None

    def close_plots(self):
        # Terminate flow/delay plot
        if self.enable_flow_delay_plot:
            self.data_queue_flow_delay.put("TERMINATE")
            self.plotter_process_flow_delay.join(timeout=5)
            if self.plotter_process_flow_delay.is_alive():
                print("Flow/Delay Plot process did not terminate in time. Terminating forcefully.")
                self.plotter_process_flow_delay.terminate()

        # Terminate cars stopped plot
        if self.enable_cars_stopped_plot:
            self.data_queue_cars_stopped.put("TERMINATE")
            self.plotter_process_cars_stopped.join(timeout=5)
            if self.plotter_process_cars_stopped.is_alive():
                print("Cars Stopped Plot process did not terminate in time. Terminating forcefully.")
                self.plotter_process_cars_stopped.terminate()

        # Terminate density/occupancy plot
        if self.enable_density_occupancy_plot:
            self.density_occupancy_queue.put("TERMINATE")
            self.density_occupancy_process.join(timeout=5)
            if self.density_occupancy_process.is_alive():
                print("Density/Occupancy plot process did not terminate in time. Terminating forcefully.")
                self.density_occupancy_process.terminate()

        # Terminate jam/queue plot
        if self.enable_jam_queue_plot:
            self.jam_queue_queue.put("TERMINATE")
            self.jam_queue_process.join(timeout=5)
            if self.jam_queue_process.is_alive():
                print("Jam/Queue plot process did not terminate in time. Terminating forcefully.")
                self.jam_queue_process.terminate()

    def plot_results(self):
        if self.enable_fuel_consumption_plot:
            self.plot_fuel_consumption()

    def plot_fuel_consumption(self):
        if not self.fuel_consumption_data:
            print("No fuel consumption data to plot.")
            return

        steps, fuel_acc, fuel_no_acc = zip(*self.fuel_consumption_data)
        print(f"Plotting fuel consumption for {len(steps)} steps.")  # Debugging output
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.set_title("Fuel Consumption Over Time")
        ax.set_xlabel("Time (steps)")
        ax.set_ylabel("Fuel Consumption (liters/s)")
        ax.plot(steps, fuel_acc, color='red', linestyle='-', label='Fuel Consumption ACC Cars')
        ax.plot(steps, fuel_no_acc, color='green', linestyle='--', label='Fuel Consumption Non-ACC Cars')
        ax.legend(loc='upper left')
        plt.tight_layout()
        plt.savefig(f"plots/fuel_consumption_over_time.png")
        plt.close()

    def update_fuel_consumption_metrics(self, step, v_acc, a_acc, v_no_acc, a_no_acc):
        if self.enable_fuel_consumption_plot:
            try:
                c1, c2, c3 = 0.00005, 0.0003, 0.0015
                fuel_acc = c1 * v_acc + c2 * a_acc + c3
                fuel_no_acc = c1 * v_no_acc + c2 * a_no_acc + c3
                self.fuel_consumption_data.append((step, fuel_acc, fuel_no_acc))
                # Debugging output
                print(f"Step: {step}, Fuel ACC: {fuel_acc}, Fuel No ACC: {fuel_no_acc}")
            except Exception as e:
                print(f"Error calculating fuel consumption: {e}")