import pygame
import sys
import numpy as np
from Car import Car
import matplotlib.pyplot as plt
from collections import deque
# Assuming the Car class is defined as above

def draw_grid(screen, road_y, L, CELL_WIDTH, WINDOW_HEIGHT, DRAW_GRID):
    if DRAW_GRID:
        # Draw vertical lines for each cell
        for i in range(L + 1):
            x = i * CELL_WIDTH
            # Draw lines spanning a portion of the window vertically
            pygame.draw.line(screen, (200, 200, 200), (x, road_y - WINDOW_HEIGHT // 4), (x, road_y + WINDOW_HEIGHT // 4), 1)

def main():
    # Simulation Parameters
    L = 100            # Length of the road (number of cells)
    N = 30             # Number of vehicles
    rho = N / L        # Traffic density
    vmax = 5           # Maximum speed
    p_fault = 0.1      # Probability of random slowdown (pfault)
    p_slow = 0.5       # Probability of slow-to-start (pslow)
    steps = 100000     # Number of simulation steps (set high for continuous simulation)
    DRAW_GRID = True   # Toggle grid visibility

    # Simulation Speed Parameters
    SIM_STEPS_PER_SECOND = 5  # Initial simulation steps per second
    last_simulation_step_time = pygame.time.get_ticks()

    # Pygame Window Dimensions
    WINDOW_WIDTH = 1600
    WINDOW_HEIGHT = 400
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("BJH Cellular Automaton Traffic Simulation with Slow-to-Stop Rule")

    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    YELLOW = (255, 255, 0)

    # Road Visualization Parameters
    ROAD_Y = WINDOW_HEIGHT // 2
    CELL_WIDTH = WINDOW_WIDTH / L  # Width of each cell in pixels
    CAR_HEIGHT = 20

    # Initialize cars without overlapping
    occupied_positions = set()
    cars = []

    for _ in range(N):
        position = np.random.randint(0, L)
        while position in occupied_positions:
            position = np.random.randint(0, L)
        occupied_positions.add(position)
        car = Car(road_length=L, cell_width=CELL_WIDTH, max_speed=vmax, p_fault=p_fault, p_slow=p_slow, position=position)
        cars.append(car)

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

    # Flow rate and stopped cars tracking
    flow_rate_window = 60  # seconds
    flow_rate = deque(maxlen=flow_rate_window)
    flow_rate_time = deque(maxlen=flow_rate_window)
    stopped_cars = deque(maxlen=flow_rate_window)

    # Initialize matplotlib plot
    plt.ion()
    fig, ax1 = plt.subplots()

    # Primary y-axis for flow rate
    ax1.set_xlabel('Time (steps)')
    ax1.set_ylabel('Flow Rate (cars/min)', color='tab:red')
    line1, = ax1.plot([], [], 'r-', label='Flow Rate')
    ax1.tick_params(axis='y', labelcolor='tab:red')

    # Secondary y-axis for stopped cars
    ax2 = ax1.twinx()
    ax2.set_ylabel('Number of Stopped Cars', color='tab:green')
    line2, = ax2.plot([], [], 'g--', label='Stopped Cars')  # Dashed line for distinction
    ax2.tick_params(axis='y', labelcolor='tab:green')

    # Add legend
    fig.legend(loc="upper right", bbox_to_anchor=(1,1), bbox_transform=ax1.transAxes)

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
                elif event.key == pygame.K_DOWN:
                    SIM_STEPS_PER_SECOND = max(1, SIM_STEPS_PER_SECOND - 1)
                elif event.key == pygame.K_g:
                    DRAW_GRID = not DRAW_GRID  # Toggle grid with 'G' key

        # --- BJH Model Update Rules ---
        if not paused and current_time - last_simulation_step_time >= 1000 / SIM_STEPS_PER_SECOND:
            # Sort cars based on positions
            cars_sorted = sorted(cars, key=lambda car: car.position)

            # Calculate distances to the next car for each car
            for i, car in enumerate(cars_sorted):
                if i < len(cars_sorted) - 1: # If not the last car
                    next_car = cars_sorted[i + 1] # Next car
                    distance = next_car.position - car.position - 1 # Distance to the next car
                    if distance < 0: # If the next car is behind
                        distance += L  # Wrap around for circular road
                else:
                    # Circular road: distance to the first car
                    next_car = cars_sorted[0] # First car
                    distance = (next_car.position + L) - car.position - 1 # Distance to the first car
                velocity_of_next_car = next_car.velocity # Velocity of the next car
                car.update_velocity(distance, velocity_of_next_car) # Update the car's velocity

            # Move cars after updating velocities to prevent influence on distance calculations
            for car in cars_sorted:
                car.move()

            # Calculate flow rate in cars per minute
            if cars:
                average_speed = np.mean([car.velocity for car in cars])
                flow_rate_value = average_speed * N * 60 / L  # Convert to cars/minute
                stopped_count = sum(car.velocity == 0 for car in cars)  # Count of stopped cars
            else:
                flow_rate_value = 0
                stopped_count = 0

            # Update flow rate and stopped cars at every timestep
            flow_rate.append(flow_rate_value)
            flow_rate_time.append(step)
            stopped_cars.append(stopped_count)

            # Update plots
            line1.set_xdata(flow_rate_time)
            line1.set_ydata(flow_rate)
            line2.set_xdata(flow_rate_time)
            line2.set_ydata(stopped_cars)

            ax1.relim()
            ax1.autoscale_view()
            ax2.relim()
            ax2.autoscale_view()

            plt.draw()
            plt.pause(0.01)

            # Increment simulation step counter
            step += 1

            # Update the last simulation step time
            last_simulation_step_time = current_time

        # --- Rendering ---

        # Fill the background
        screen.fill(WHITE)

        # Draw the road line
        pygame.draw.line(screen, BLACK, (0, ROAD_Y), (WINDOW_WIDTH, ROAD_Y), 2)

        # Draw the grid if enabled
        draw_grid(screen, ROAD_Y, L, CELL_WIDTH, WINDOW_HEIGHT, DRAW_GRID)

        # Draw each car
        for car in cars:
            car.draw(screen, ROAD_Y, CAR_HEIGHT)

        # --- Display Simulation Statistics ---

        # Calculate statistics
        if cars:
            average_speed = np.mean([car.velocity for car in cars])
            stopped_vehicles = np.sum([car.velocity == 0 for car in cars])
        else:
            average_speed = 0
            stopped_vehicles = 0

        # Render statistics text
        stats_text = f"Step: {step} | Sim Steps/sec: {SIM_STEPS_PER_SECOND} | Avg Speed: {average_speed:.2f} | Stopped: {stopped_vehicles}"
        text_surface = font.render(stats_text, True, BLACK)
        screen.blit(text_surface, (10, 10))

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
    for idx, car in enumerate(cars):
        print(f"Car {idx + 1}:")
        print(f"  Total Distance Traveled: {car.total_distance}")
        print(f"  Number of Stops: {car.stops}")
        print(f"  Time in Traffic: {car.time_in_traffic} steps\n")

    # Quit Pygame
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
