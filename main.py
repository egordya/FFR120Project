import pygame
import sys
import numpy as np
from Car import Car
import matplotlib.pyplot as plt
from collections import deque
import threading
import time

def draw_grid(screen, road_y, L, CELL_WIDTH, WINDOW_HEIGHT, DRAW_GRID):
    if DRAW_GRID:
        # Draw vertical lines for each cell
        for i in range(L + 1):
            x = i * CELL_WIDTH
            # Draw lines spanning a portion of the window vertically
            pygame.draw.line(screen, (200, 200, 200), (x, road_y - WINDOW_HEIGHT // 8), (x, road_y + WINDOW_HEIGHT // 8), 1)

def main():
    # Simulation Parameters
    L = 100            # Length of the road (number of cells)
    N = 30             # Number of vehicles per road
    vmax = 2           # Maximum speed
    p_fault = 0.1      # Probability of random slowdown (pfault)
    p_slow = 0.5       # Probability of slow-to-start (pslow)
    steps = 100000     # Number of simulation steps (set high for continuous simulation)
    DRAW_GRID = True   # Toggle grid visibility

    # Simulation Speed Parameters
    SIM_STEPS_PER_SECOND = 20  # Increased simulation steps per second for smoother updates
    SIMULATION_STEP_INTERVAL = 1000 / SIM_STEPS_PER_SECOND  # in milliseconds

    # Percentage of cars with cruise control on Road 1
    cruise_control_percentage_road1 = 100

    # Pygame Window Dimensions
    WINDOW_WIDTH = 1600
    WINDOW_HEIGHT = 800
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("BJH Cellular Automaton Traffic Simulation with Two Roads")

    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)

    # Road Visualization Parameters
    ROAD_Y_TOP = WINDOW_HEIGHT // 3  # Y-coordinate for the top road
    ROAD_Y_BOTTOM = 2 * WINDOW_HEIGHT // 3  # Y-coordinate for the bottom road
    CELL_WIDTH = WINDOW_WIDTH / L  # Width of each cell in pixels
    CAR_HEIGHT = 20

    # Initialize cars for Road 1 (with a percentage of cars having cruise control)
    occupied_positions_road1 = set()
    cars_road1 = []

    for _ in range(N):
        position = np.random.randint(0, L)
        while position in occupied_positions_road1:
            position = np.random.randint(0, L)
        occupied_positions_road1.add(position)

        # Decide whether this car has cruise control based on the specified percentage
        if np.random.rand() < (cruise_control_percentage_road1 / 100):
            cruise_control = True
        else:
            cruise_control = False

        car = Car(road_length=L, cell_width=CELL_WIDTH, max_speed=vmax, p_fault=p_fault, p_slow=p_slow,
                  position=position, cruise_control=cruise_control)
        cars_road1.append(car)

    # Initialize cars for Road 2 (without cruise control)
    occupied_positions_road2 = set()
    cars_road2 = []

    for _ in range(N):
        position = np.random.randint(0, L)
        while position in occupied_positions_road2:
            position = np.random.randint(0, L)
        occupied_positions_road2.add(position)

        car = Car(road_length=L, cell_width=CELL_WIDTH, max_speed=vmax, p_fault=p_fault, p_slow=p_slow,
                  position=position, cruise_control=False)
        cars_road2.append(car)

    # Control Variables
    paused = False

    # Font for displaying simulation stats
    pygame.font.init()
    font = pygame.font.SysFont(None, 24)

    # Clock to control rendering speed
    clock = pygame.time.Clock()
    FPS = 60  # Frames per second

    running = True
    step = 0

    # Flow rate and stopped cars tracking for both roads
    flow_rate_window = 300  # number of data points to keep
    flow_rate_road1 = deque(maxlen=flow_rate_window)
    flow_rate_time_road1 = deque(maxlen=flow_rate_window)
    stopped_cars_road1 = deque(maxlen=flow_rate_window)

    flow_rate_road2 = deque(maxlen=flow_rate_window)
    flow_rate_time_road2 = deque(maxlen=flow_rate_window)
    stopped_cars_road2 = deque(maxlen=flow_rate_window)

    # Initialize matplotlib plots for both roads with blitting
    plt.ion()
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))
    fig.tight_layout(pad=3.0)

    # Road 1 Plot
    ax1.set_title('Road 1 (Cruise Control)')
    ax1.set_xlabel('Time (steps)')
    ax1.set_ylabel('Flow Rate (cars/min)', color='tab:red')
    line1_road1, = ax1.plot([], [], 'r-', label='Flow Rate')
    ax1.tick_params(axis='y', labelcolor='tab:red')

    ax1b = ax1.twinx()
    ax1b.set_ylabel('Number of Stopped Cars', color='tab:green')
    line2_road1, = ax1b.plot([], [], 'g--', label='Stopped Cars')
    ax1b.tick_params(axis='y', labelcolor='tab:green')

    ax1.legend(loc='upper left')

    # Road 2 Plot
    ax2.set_title('Road 2 (No Cruise Control)')
    ax2.set_xlabel('Time (steps)')
    ax2.set_ylabel('Flow Rate (cars/min)', color='tab:red')
    line1_road2, = ax2.plot([], [], 'r-', label='Flow Rate')
    ax2.tick_params(axis='y', labelcolor='tab:red')

    ax2b = ax2.twinx()
    ax2b.set_ylabel('Number of Stopped Cars', color='tab:green')
    line2_road2, = ax2b.plot([], [], 'g--', label='Stopped Cars')
    ax2b.tick_params(axis='y', labelcolor='tab:green')

    ax2.legend(loc='upper left')

    # Draw the canvas once, and cache the background
    fig.canvas.draw()
    plt.show(block=False)
    background1 = fig.canvas.copy_from_bbox(ax1.bbox)
    background2 = fig.canvas.copy_from_bbox(ax2.bbox)

    def update_plots():
        while running:
            if not paused:
                # Restore the background
                fig.canvas.restore_region(background1)
                fig.canvas.restore_region(background2)

                # Update data for Road 1
                line1_road1.set_xdata(flow_rate_time_road1)
                line1_road1.set_ydata(flow_rate_road1)
                line2_road1.set_xdata(flow_rate_time_road1)
                line2_road1.set_ydata(stopped_cars_road1)

                ax1.draw_artist(line1_road1)
                ax1b.draw_artist(line2_road1)

                # Update data for Road 2
                line1_road2.set_xdata(flow_rate_time_road2)
                line1_road2.set_ydata(flow_rate_road2)
                line2_road2.set_xdata(flow_rate_time_road2)
                line2_road2.set_ydata(stopped_cars_road2)

                ax2.draw_artist(line1_road2)
                ax2b.draw_artist(line2_road2)

                # Blit the updated artists
                fig.canvas.blit(ax1.bbox)
                fig.canvas.blit(ax1b.bbox)
                fig.canvas.blit(ax2.bbox)
                fig.canvas.blit(ax2b.bbox)

                fig.canvas.flush_events()
                time.sleep(0.5)  # Update plots every 0.5 seconds

    # Start the plotting thread
    plot_thread = threading.Thread(target=update_plots)
    plot_thread.daemon = True
    plot_thread.start()

    last_simulation_step_time = pygame.time.get_ticks()

    while running and step < steps:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_UP:
                    SIM_STEPS_PER_SECOND += 1
                    SIMULATION_STEP_INTERVAL = 1000 / SIM_STEPS_PER_SECOND
                elif event.key == pygame.K_DOWN:
                    SIM_STEPS_PER_SECOND = max(1, SIM_STEPS_PER_SECOND - 1)
                    SIMULATION_STEP_INTERVAL = 1000 / SIM_STEPS_PER_SECOND
                elif event.key == pygame.K_g:
                    DRAW_GRID = not DRAW_GRID  # Toggle grid with 'G' key

        # --- BJH Model Update Rules ---
        if not paused and current_time - last_simulation_step_time >= SIMULATION_STEP_INTERVAL:
            # Update Road 1
            cars_sorted_road1 = sorted(cars_road1, key=lambda car: car.position)


            # This loop basically updates the velocity of each car based on the BJH model and then moves the car in an array
            # The array is sorted based on the position of the cars
            for i, car in enumerate(cars_sorted_road1):
                if i < len(cars_sorted_road1) - 1:
                    next_car = cars_sorted_road1[i + 1]
                    distance = next_car.position - car.position - 1
                    if distance < 0:
                        distance += L
                else:
                    next_car = cars_sorted_road1[0]
                    distance = (next_car.position + L) - car.position - 1
                velocity_of_next_car = next_car.velocity
                car.update_velocity(distance, velocity_of_next_car)

            for car in cars_sorted_road1:
                car.move()

            # Update Road 2
            cars_sorted_road2 = sorted(cars_road2, key=lambda car: car.position)


            for i, car in enumerate(cars_sorted_road2):
                if i < len(cars_sorted_road2) - 1:
                    next_car = cars_sorted_road2[i + 1]
                    distance = next_car.position - car.position - 1
                    if distance < 0:
                        distance += L
                else:
                    next_car = cars_sorted_road2[0]
                    distance = (next_car.position + L) - car.position - 1
                velocity_of_next_car = next_car.velocity
                car.update_velocity(distance, velocity_of_next_car)

            for car in cars_sorted_road2:
                car.move()

            # Calculate flow rate and stopped cars for Road 1
            if cars_road1:
                average_speed = np.mean([car.velocity for car in cars_road1])
                flow_rate_value = average_speed * N * 60 / L  # Convert to cars/minute
                stopped_count = sum(car.velocity == 0 for car in cars_road1)
            else:
                flow_rate_value = 0
                stopped_count = 0

            flow_rate_road1.append(flow_rate_value)
            flow_rate_time_road1.append(step)
            stopped_cars_road1.append(stopped_count)

            # Calculate flow rate and stopped cars for Road 2
            if cars_road2:
                average_speed = np.mean([car.velocity for car in cars_road2])
                flow_rate_value = average_speed * N * 60 / L  # Convert to cars/minute
                stopped_count = sum(car.velocity == 0 for car in cars_road2)
            else:
                flow_rate_value = 0
                stopped_count = 0

            flow_rate_road2.append(flow_rate_value)
            flow_rate_time_road2.append(step)
            stopped_cars_road2.append(stopped_count)

            # Increment simulation step counter
            step += 1

            # Update the last simulation step time
            last_simulation_step_time = current_time

        # --- Rendering ---

        # Fill the background
        screen.fill(WHITE)

        # Draw the roads
        pygame.draw.line(screen, BLACK, (0, ROAD_Y_TOP), (WINDOW_WIDTH, ROAD_Y_TOP), 2)
        pygame.draw.line(screen, BLACK, (0, ROAD_Y_BOTTOM), (WINDOW_WIDTH, ROAD_Y_BOTTOM), 2)

        # Draw the grid if enabled
        draw_grid(screen, ROAD_Y_TOP, L, CELL_WIDTH, WINDOW_HEIGHT, DRAW_GRID)
        draw_grid(screen, ROAD_Y_BOTTOM, L, CELL_WIDTH, WINDOW_HEIGHT, DRAW_GRID)

        # Draw each car on Road 1
        for car in cars_road1:
            car.draw(screen, ROAD_Y_TOP, CAR_HEIGHT)

        # Draw each car on Road 2
        for car in cars_road2:
            car.draw(screen, ROAD_Y_BOTTOM, CAR_HEIGHT)

        # --- Display Simulation Statistics ---

        # Road 1 Statistics
        if cars_road1:
            average_speed_road1 = np.mean([car.velocity for car in cars_road1])
            stopped_vehicles_road1 = np.sum([car.velocity == 0 for car in cars_road1])
        else:
            average_speed_road1 = 0
            stopped_vehicles_road1 = 0

        stats_text_road1 = f"Road 1 - Step: {step} | Avg Speed: {average_speed_road1:.2f} | Stopped: {stopped_vehicles_road1}"
        text_surface_road1 = font.render(stats_text_road1, True, BLACK)
        screen.blit(text_surface_road1, (10, 10))

        # Road 2 Statistics
        if cars_road2:
            average_speed_road2 = np.mean([car.velocity for car in cars_road2])
            stopped_vehicles_road2 = np.sum([car.velocity == 0 for car in cars_road2])
        else:
            average_speed_road2 = 0
            stopped_vehicles_road2 = 0

        stats_text_road2 = f"Road 2 - Step: {step} | Avg Speed: {average_speed_road2:.2f} | Stopped: {stopped_vehicles_road2}"
        text_surface_road2 = font.render(stats_text_road2, True, BLACK)
        screen.blit(text_surface_road2, (10, WINDOW_HEIGHT // 2 + 10))

        # Render grid status
        grid_status = "ON" if DRAW_GRID else "OFF"
        grid_text = f"Grid: {grid_status} (Press 'G' to toggle)"
        grid_surface = font.render(grid_text, True, BLACK)
        screen.blit(grid_surface, (10, 30))

        # Render paused status
        if paused:
            paused_text = font.render("PAUSED", True, RED)
            screen.blit(paused_text, (WINDOW_WIDTH - 100, 10))

        # Update the display
        pygame.display.flip()

        # Control the rendering speed
        clock.tick(FPS)

    # After simulation ends, print individual car metrics (optional)
    print("\nSimulation Ended.\n")
    # Road 1 Metrics
    print("Road 1 Car Metrics:")
    for idx, car in enumerate(cars_road1):
        print(f"Car {idx + 1}:")
        print(f"  Total Distance Traveled: {car.total_distance}")
        print(f"  Number of Stops: {car.stops}")
        print(f"  Time in Traffic: {car.time_in_traffic} steps\n")

    # Road 2 Metrics
    print("Road 2 Car Metrics:")
    for idx, car in enumerate(cars_road2):
        print(f"Car {idx + 1}:")
        print(f"  Total Distance Traveled: {car.total_distance}")
        print(f"  Number of Stops: {car.stops}")
        print(f"  Time in Traffic: {car.time_in_traffic} steps\n")

    # Quit Pygame
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
