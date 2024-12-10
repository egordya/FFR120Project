import os
import seaborn as sns
import matplotlib.pyplot as plt
from collections import deque
import multiprocessing
import sys
import queue

COLOR_RED = "#E53D00"
COLOR_YELLOW = "#FFE900"
COLOR_TEAL = "#21A0A0"
COLOR_DARKTEAL = "#046865"
COLOR_DARKGREY = "#A9A9A9"
COLOR_WHITE = "#FCFFF7"

sns.set_style("darkgrid")

def plot_process(data_queue, control_queue, N, L):
    plt.ion()
    fig, (ax1, ax3) = plt.subplots(1, 2, figsize=(14, 6))

    flow_rate_window = 60
    flow_rate_road1 = deque(maxlen=flow_rate_window)
    flow_rate_road2 = deque(maxlen=flow_rate_window)
    flow_rate_time = deque(maxlen=flow_rate_window)
    delay_percentage_road1 = deque(maxlen=flow_rate_window)
    delay_percentage_road2 = deque(maxlen=flow_rate_window)
    stopped_cars_road1 = deque(maxlen=flow_rate_window)
    stopped_cars_road2 = deque(maxlen=flow_rate_window)

    ax1.set_xlabel('Time (steps)')
    ax1.set_ylabel('Flow Rate (cars/min)', color=COLOR_RED)
    line1_road1, = ax1.plot([], [], color=COLOR_RED, linestyle='-', label='Flow Rate Road 1')
    line1_road2, = ax1.plot([], [], color=COLOR_DARKGREY, linestyle='--', label='Flow Rate Road 2')
    ax1.tick_params(axis='y', labelcolor=COLOR_RED)
    ax1.set_ylim(0, 100)

    ax2 = ax1.twinx()
    ax2.set_ylabel('Average Delay (%)', color=COLOR_TEAL)
    line2_road1, = ax2.plot([], [], color=COLOR_TEAL, linestyle='-', label='Delay Road 1')
    line2_road2, = ax2.plot([], [], color=COLOR_DARKTEAL, linestyle='--', label='Delay Road 2')
    ax2.tick_params(axis='y', labelcolor=COLOR_TEAL)
    ax2.set_ylim(0, 300)

    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left')

    ax3.set_title('Number of Stopped Cars')
    ax3.set_xlabel('Roads')
    ax3.set_ylabel('Number of Stopped Cars')
    bars = ax3.bar(['Road 1', 'Road 2'], [0, 0], color=[COLOR_TEAL, COLOR_DARKTEAL])
    ax3.set_ylim(0, N)

    def on_key_press(event):
        if event.key == 'escape':
            print("ESC pressed in plot window. Sending termination signal.")
            control_queue.put("TERMINATE_FROM_PLOT")
            plt.close(fig)

    fig.canvas.mpl_connect('key_press_event', on_key_press)

    save_steps = {100, 300, 500}
    plt.tight_layout()
    plt.show()

    while True:
        try:
            data = data_queue.get(timeout=0.1)
            if data == "TERMINATE":
                print("Plot process received termination signal.")
                break

            step, fr1, fr2, d1, d2, sc1, sc2 = data
            flow_rate_time.append(step)
            flow_rate_road1.append(fr1)
            flow_rate_road2.append(fr2)
            delay_percentage_road1.append(d1)
            delay_percentage_road2.append(d2)
            stopped_cars_road1.append(sc1)
            stopped_cars_road2.append(sc2)

            line1_road1.set_data(flow_rate_time, flow_rate_road1)
            line1_road2.set_data(flow_rate_time, flow_rate_road2)
            line2_road1.set_data(flow_rate_time, delay_percentage_road1)
            line2_road2.set_data(flow_rate_time, delay_percentage_road2)

            ax1.relim()
            ax1.autoscale_view()
            ax2.relim()
            ax2.autoscale_view()

            if stopped_cars_road1:
                bars[0].set_height(stopped_cars_road1[-1])
            if stopped_cars_road2:
                bars[1].set_height(stopped_cars_road2[-1])

            if step in save_steps:
                os.makedirs("plots", exist_ok=True)
                plt.savefig(f"plots/plot_step_{step}.png", dpi=300)
                print(f"Saved plot for step {step}.")

            fig.canvas.draw_idle()
            fig.canvas.flush_events()
            plt.pause(0.001)

        except queue.Empty:
            pass
        except Exception as e:
            print(f"Plot process encountered an error: {e}")
            break

    plt.close(fig)
    sys.exit()

def density_occupancy_plot_process(data_queue, control_queue):
    plt.ion()
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_title("Density and Occupancy Over Time")
    ax.set_xlabel("Time (steps)")
    ax.set_ylabel("Density (veh/cell)", color=COLOR_RED)
    ax.set_ylim(0, 1)

    ax2 = ax.twinx()
    ax2.set_ylabel("Occupancy (%)", color=COLOR_TEAL)
    ax2.set_ylim(0, 100)

    time_data = deque(maxlen=300)

    density_data_r1 = deque(maxlen=300)
    density_data_r2 = deque(maxlen=300)
    occupancy_data_r1 = deque(maxlen=300)
    occupancy_data_r2 = deque(maxlen=300)

    line_density_r1, = ax.plot([], [], color=COLOR_RED, linestyle='-', label='Density Road 1')
    line_density_r2, = ax.plot([], [], color=COLOR_DARKGREY, linestyle='--', label='Density Road 2')
    line_occupancy_r1, = ax2.plot([], [], color=COLOR_TEAL, linestyle='-', label='Occupancy Road 1')
    line_occupancy_r2, = ax2.plot([], [], color=COLOR_DARKTEAL, linestyle='--', label='Occupancy Road 2')

    lines_1, labels_1 = ax.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left')

    def on_key_press(event):
        if event.key == 'escape':
            print("ESC pressed in density/occupancy plot window. Sending termination signal.")
            control_queue.put("TERMINATE_FROM_PLOT")
            plt.close(fig)

    fig.canvas.mpl_connect('key_press_event', on_key_press)

    plt.tight_layout()
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
    ax.set_ylim(0, 50)

    ax2 = ax.twinx()
    ax2.set_ylabel("Queue Duration (steps)", color=COLOR_TEAL)
    ax2.set_ylim(0, 300)

    time_data = deque(maxlen=300)
    jam_length_r1 = deque(maxlen=300)
    jam_length_r2 = deque(maxlen=300)
    queue_duration_r1 = deque(maxlen=300)
    queue_duration_r2 = deque(maxlen=300)

    line_jam_r1, = ax.plot([], [], color=COLOR_RED, linestyle='-', label='Jam Length Road 1')
    line_jam_r2, = ax.plot([], [], color=COLOR_DARKGREY, linestyle='--', label='Jam Length Road 2')

    line_queue_r1, = ax2.plot([], [], color=COLOR_TEAL, linestyle='-', label='Queue Dur. Road 1')
    line_queue_r2, = ax2.plot([], [], color=COLOR_DARKTEAL, linestyle='--', label='Queue Dur. Road 2')

    lines_1, labels_1 = ax.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left')

    def on_key_press(event):
        if event.key == 'escape':
            print("ESC pressed in jam/queue plot window. Sending termination signal.")
            control_queue.put("TERMINATE_FROM_PLOT")
            plt.close(fig)

    fig.canvas.mpl_connect('key_press_event', on_key_press)

    plt.tight_layout()
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
    def __init__(self, N, L,
                 enable_main_plot=True,
                 enable_density_occupancy_plot=True,
                 enable_jam_queue_plot=True):
        self.N = N
        self.L = L
        self.enable_main_plot = enable_main_plot
        self.enable_density_occupancy_plot = enable_density_occupancy_plot
        self.enable_jam_queue_plot = enable_jam_queue_plot

        self.data_queue = None
        self.control_queue = None
        self.plotter_process = None

        # Main Plot (Flow/Delay/Stops)
        if self.enable_main_plot:
            self.data_queue = multiprocessing.Queue()
            self.control_queue = multiprocessing.Queue()
            self.plotter_process = multiprocessing.Process(target=plot_process, args=(self.data_queue, self.control_queue, N, L))
            self.plotter_process.start()

        # Density/Occupancy Plot
        self.density_occupancy_queue = None
        self.density_occupancy_control_queue = None
        self.density_occupancy_process = None
        if self.enable_density_occupancy_plot:
            self.density_occupancy_queue = multiprocessing.Queue()
            self.density_occupancy_control_queue = multiprocessing.Queue()
            self.density_occupancy_process = multiprocessing.Process(
                target=density_occupancy_plot_process,
                args=(self.density_occupancy_queue, self.density_occupancy_control_queue)
            )
            self.density_occupancy_process.start()

        # Jam/Queue Plot
        self.jam_queue_queue = None
        self.jam_queue_control_queue = None
        self.jam_queue_process = None
        if self.enable_jam_queue_plot:
            self.jam_queue_queue = multiprocessing.Queue()
            self.jam_queue_control_queue = multiprocessing.Queue()
            self.jam_queue_process = multiprocessing.Process(
                target=jam_queue_plot_process,
                args=(self.jam_queue_queue, self.jam_queue_control_queue)
            )
            self.jam_queue_process.start()

    def update_metrics(self, step, flow_rate_value_road1, flow_rate_value_road2,
                       delay_road1, delay_road2,
                       stopped_cars_count_road1, stopped_cars_count_road2):
        if self.enable_main_plot:
            try:
                self.data_queue.put((step, flow_rate_value_road1, flow_rate_value_road2,
                                     delay_road1, delay_road2,
                                     stopped_cars_count_road1, stopped_cars_count_road2))
            except Exception as e:
                print(f"Error sending data to main plotter: {e}")

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
        # Check main plot
        if self.enable_main_plot:
            try:
                message = self.control_queue.get_nowait()
                return message
            except queue.Empty:
                pass
            except Exception as e:
                print(f"Error reading control messages from main plot: {e}")

        # Check density/occupancy plot
        if self.enable_density_occupancy_plot:
            try:
                second_msg = self.density_occupancy_control_queue.get_nowait()
                return second_msg
            except queue.Empty:
                pass
            except Exception as e:
                print(f"Error reading density/occupancy control messages: {e}")

        # Check jam/queue plot
        if self.enable_jam_queue_plot:
            try:
                third_msg = self.jam_queue_control_queue.get_nowait()
                return third_msg
            except queue.Empty:
                pass
            except Exception as e:
                print(f"Error reading jam/queue control messages: {e}")

        return None

    def close_plots(self):
        # Terminate main plot
        if self.enable_main_plot:
            self.data_queue.put("TERMINATE")
            self.plotter_process.join(timeout=5)
            if self.plotter_process.is_alive():
                print("Main Plot process did not terminate in time. Terminating forcefully.")
                self.plotter_process.terminate()

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
