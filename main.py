import pygame
import sys
import numpy as np
from Car import Car
from MeasurementAndPlotter import MeasurementAndPlotter

def draw_grid(screen, road_y, L, CELL_WIDTH, WINDOW_HEIGHT, DRAW_GRID):
    if DRAW_GRID:
        # Draw vertical lines for each cell
        for i in range(L + 1):
            x = i * CELL_WIDTH
            pygame.draw.line(screen, (200, 200, 200), (x, road_y - WINDOW_HEIGHT // 8), (x, road_y + WINDOW_HEIGHT // 8), 1)

def compute_jam_length_and_queue_duration(road_length, cars, previous_queue_duration):
    # Create a boolean array for stopped cars
    stopped = np.zeros(road_length, dtype=bool)
    for car in cars:
        if car.velocity == 0:
            stopped[car.position] = True

    # Find longest contiguous sequence of True values in a circular array
    max_run = 0
    current_run = 0
    for i in range(road_length):
        if stopped[i]:
            current_run += 1
            if current_run > max_run:
                max_run = current_run
        else:
            current_run = 0

    # Check wrap-around continuity if both ends are True
    if stopped[0] and stopped[-1]:
        start_run = 0
        i = 0
        while i < road_length and stopped[i]:
            start_run += 1
            i += 1
        end_run = 0
        i = road_length - 1
        while i >= 0 and stopped[i]:
            end_run += 1
            i -= 1
        if start_run + end_run > max_run:
            max_run = start_run + end_run

    # Queue duration logic
    # If jam_length > 0, increment queue duration, else reset
    if max_run > 0:
        queue_duration = previous_queue_duration + 1
    else:
        queue_duration = 0

    return max_run, queue_duration

def main():
    # Simulation Parameters
    L = 140            # Length of the road (number of cells)
    N = 20            # Number of vehicles per road
    vmax = 4          # Maximum speed
    p_fault = 0.1     # Probability of random slowdown (pfault)
    p_slow = 0.5      # Probability of slow-to-start (pslow)
    steps = 100000    # Number of simulation steps
    DRAW_GRID = True  # Toggle grid visibility

    SIM_STEPS_PER_SECOND = 20
    SIMULATION_STEP_INTERVAL = 1000 / SIM_STEPS_PER_SECOND

    cruise_control_percentage_road1 = 100  # All cars on Road 1 have ACC

    # Pygame Setup
    pygame.init()  # Initialize Pygame
    WINDOW_WIDTH = 2500
    WINDOW_HEIGHT = 800
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Traffic Simulation with Three Plots")

    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    DODGERBLUE = (30, 144, 255)

    # Road Visualization
    ROAD_Y_TOP = WINDOW_HEIGHT // 3
    ROAD_Y_BOTTOM = 2 * WINDOW_HEIGHT // 3
    CELL_WIDTH = WINDOW_WIDTH / L
    CAR_HEIGHT = 20

    # Initialize Road 1
    occupied_positions_road1 = set()
    cars_road1 = []
    for _ in range(N):
        position = np.random.randint(0, L)
        while position in occupied_positions_road1:
            position = np.random.randint(0, L)
        occupied_positions_road1.add(position)
        # Determine if ACC is enabled for this car
        acc_enabled = (np.random.rand() < (cruise_control_percentage_road1 / 100))
        car = Car(road_length=L, cell_width=CELL_WIDTH, max_speed=vmax, p_fault=p_fault, p_slow=p_slow,
                  position=position, adaptive_cruise_control=acc_enabled)
        cars_road1.append(car)

    # Initialize Road 2
    occupied_positions_road2 = set()
    cars_road2 = []
    for _ in range(N):
        position = np.random.randint(0, L)
        while position in occupied_positions_road2:
            position = np.random.randint(0, L)
        occupied_positions_road2.add(position)
        # Road 2 cars are not ACC
        car = Car(road_length=L, cell_width=CELL_WIDTH, max_speed=vmax, p_fault=p_fault, p_slow=p_slow,
                  position=position, adaptive_cruise_control=False)
        cars_road2.append(car)

    paused = False
    pygame.font.init()
    font = pygame.font.SysFont(None, 24)
    clock = pygame.time.Clock()
    FPS = 60
    running = True
    step = 0

    # Instantiate measurement and plotting helper
    # Enable or disable plots here:
    enable_main_plot = True
    enable_density_occupancy_plot = False
    enable_jam_queue_plot = False

    measurement = MeasurementAndPlotter(N, L,
                                        enable_main_plot=enable_main_plot,
                                        enable_density_occupancy_plot=enable_density_occupancy_plot,
                                        enable_jam_queue_plot=enable_jam_queue_plot)

    last_simulation_step_time = pygame.time.get_ticks()

    # For jam length and queue duration tracking
    queue_duration_road1 = 0
    queue_duration_road2 = 0

    try:
        while running and step < steps:
            current_time = pygame.time.get_ticks()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("Pygame QUIT event detected. Exiting simulation.")
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        paused = not paused
                        print(f"Simulation {'paused' if paused else 'resumed'}.")
                    elif event.key == pygame.K_UP:
                        SIM_STEPS_PER_SECOND += 1
                        SIMULATION_STEP_INTERVAL = 1000 / SIM_STEPS_PER_SECOND
                        print(f"Simulation speed increased to {SIM_STEPS_PER_SECOND} steps per second.")
                    elif event.key == pygame.K_DOWN:
                        SIM_STEPS_PER_SECOND = max(1, SIM_STEPS_PER_SECOND - 1)
                        SIMULATION_STEP_INTERVAL = 1000 / SIM_STEPS_PER_SECOND
                        print(f"Simulation speed decreased to {SIM_STEPS_PER_SECOND} steps per second.")
                    elif event.key == pygame.K_g:
                        DRAW_GRID = not DRAW_GRID
                        print(f"Grid {'enabled' if DRAW_GRID else 'disabled'}.")
                    elif event.key == pygame.K_ESCAPE:
                        print("ESC pressed in simulation window. Exiting simulation.")
                        running = False

            # Check for control messages from plot windows
            control_message = measurement.check_control_messages()
            if control_message == "TERMINATE_FROM_PLOT":
                print("Termination signal received from plot window. Exiting simulation.")
                running = False

            if not paused and current_time - last_simulation_step_time >= SIMULATION_STEP_INTERVAL:
                # Update Road 1
                cars_sorted_road1 = sorted(cars_road1, key=lambda car: car.position)
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

                # Compute metrics
                # Road 1
                if cars_road1:
                    average_speed_road1 = np.mean([car.velocity for car in cars_road1])
                    flow_rate_value_road1 = average_speed_road1 * N * 60 / L
                    delays_road1 = []
                    for car in cars_road1:
                        if car.total_distance > 0:
                            ideal_time = car.total_distance / vmax
                            delay = ((car.time_in_traffic - ideal_time) / ideal_time) * 100
                            delays_road1.append(delay)
                    delay_road1 = np.mean(delays_road1) if delays_road1 else 0
                else:
                    flow_rate_value_road1 = 0
                    delay_road1 = 0

                # Road 2
                if cars_road2:
                    average_speed_road2 = np.mean([car.velocity for car in cars_road2])
                    flow_rate_value_road2 = average_speed_road2 * N * 60 / L
                    delays_road2 = []
                    for car in cars_road2:
                        if car.total_distance > 0:
                            ideal_time = car.total_distance / vmax
                            delay = ((car.time_in_traffic - ideal_time) / ideal_time) * 100
                            delays_road2.append(delay)
                    delay_road2 = np.mean(delays_road2) if delays_road2 else 0
                else:
                    flow_rate_value_road2 = 0
                    delay_road2 = 0

                # Density and Occupancy Road 1
                num_cars_road1 = len(cars_road1)
                density_road1 = num_cars_road1 / L
                occupied_positions_road1 = set([car.position for car in cars_road1])
                occupancy_road1 = (len(occupied_positions_road1) / L) * 100.0

                # Density and Occupancy Road 2
                num_cars_road2 = len(cars_road2)
                density_road2 = num_cars_road2 / L
                occupied_positions_road2 = set([car.position for car in cars_road2])
                occupancy_road2 = (len(occupied_positions_road2) / L) * 100.0

                # Jam Length and Queue Duration for Road 1
                jam_length_road1, queue_duration_road1 = compute_jam_length_and_queue_duration(
                    L, cars_road1, queue_duration_road1)

                # Jam Length and Queue Duration for Road 2
                jam_length_road2, queue_duration_road2 = compute_jam_length_and_queue_duration(
                    L, cars_road2, queue_duration_road2)

                # Update density/occupancy data
                measurement.update_density_occupancy(step, density_road1, occupancy_road1, density_road2, occupancy_road2)

                stopped_cars_count_road1 = np.sum([car.velocity == 0 for car in cars_road1])
                stopped_cars_count_road2 = np.sum([car.velocity == 0 for car in cars_road2])

                # Update main metrics plot
                measurement.update_metrics(step,
                                           flow_rate_value_road1, flow_rate_value_road2,
                                           delay_road1, delay_road2,
                                           stopped_cars_count_road1, stopped_cars_count_road2)

                # Update jam/queue metrics plot
                measurement.update_jam_queue_metrics(step,
                                                     jam_length_road1, jam_length_road2,
                                                     queue_duration_road1, queue_duration_road2)

                print(f"Step: {step}, FR1: {flow_rate_value_road1:.2f}, D1: {delay_road1:.2f}, "
                      f"FR2: {flow_rate_value_road2:.2f}, D2: {delay_road2:.2f}")
                print(f"Jam Road 1: {jam_length_road1}, QD1: {queue_duration_road1}, "
                      f"Jam Road 2: {jam_length_road2}, QD2: {queue_duration_road2}")

                # Increment step
                step += 1
                last_simulation_step_time = current_time

            # --- Rendering ---
            screen.fill(WHITE)
            pygame.draw.line(screen, BLACK, (0, ROAD_Y_TOP), (WINDOW_WIDTH, ROAD_Y_TOP), 2)
            pygame.draw.line(screen, BLACK, (0, ROAD_Y_BOTTOM), (WINDOW_WIDTH, ROAD_Y_BOTTOM), 2)
            draw_grid(screen, ROAD_Y_TOP, L, CELL_WIDTH, WINDOW_HEIGHT, DRAW_GRID)
            draw_grid(screen, ROAD_Y_BOTTOM, L, CELL_WIDTH, WINDOW_HEIGHT, DRAW_GRID)

            for car in cars_road1:
                car.draw(screen, ROAD_Y_TOP, CAR_HEIGHT)

            for car in cars_road2:
                car.draw(screen, ROAD_Y_BOTTOM, CAR_HEIGHT)

            # Display Statistics on Screen
            if cars_road1:
                average_speed_road1 = np.mean([car.velocity for car in cars_road1])
                stopped_vehicles_road1 = np.sum([car.velocity == 0 for car in cars_road1])
            else:
                average_speed_road1 = 0
                stopped_vehicles_road1 = 0

            if cars_road2:
                average_speed_road2 = np.mean([car.velocity for car in cars_road2])
                stopped_vehicles_road2 = np.sum([car.velocity == 0 for car in cars_road2])
            else:
                average_speed_road2 = 0
                stopped_vehicles_road2 = 0

            stats_text_road1 = f"Road 1 - Step: {step} | Avg Speed: {average_speed_road1:.2f} | Stopped: {stopped_vehicles_road1}"
            text_surface_road1 = font.render(stats_text_road1, True, DODGERBLUE)
            screen.blit(text_surface_road1, (10, 10))

            stats_text_road2 = f"Road 2 - Step: {step} | Avg Speed: {average_speed_road2:.2f} | Stopped: {stopped_vehicles_road2}"
            text_surface_road2 = font.render(stats_text_road2, True, BLACK)
            screen.blit(text_surface_road2, (10, WINDOW_HEIGHT // 2 + 10))

            grid_status = "ON" if DRAW_GRID else "OFF"
            grid_text = f"Grid: {grid_status} (Press 'G' to toggle)"
            grid_surface = font.render(grid_text, True, BLACK)
            screen.blit(grid_surface, (10, 30))

            if paused:
                paused_text = font.render("PAUSED", True, RED)
                screen.blit(paused_text, (WINDOW_WIDTH - 100, 10))

            pygame.display.flip()
            clock.tick(FPS)

    except KeyboardInterrupt:
        print("\nKeyboard Interrupt detected. Exiting...")
    finally:
        print("\nSimulation Ended.\n")
        print("Road 1 Car Metrics:")
        for idx, car in enumerate(cars_road1):
            print(f"Car {idx + 1}:")
            print(f"  Total Distance Traveled: {car.total_distance}")
            print(f"  Number of Stops: {car.stops}")
            print(f"  Time in Traffic: {car.time_in_traffic} steps\n")

        print("Road 2 Car Metrics:")
        for idx, car in enumerate(cars_road2):
            print(f"Car {idx + 1}:")
            print(f"  Total Distance Traveled: {car.total_distance}")
            print(f"  Number of Stops: {car.stops}")
            print(f"  Time in Traffic: {car.time_in_traffic} steps\n")

        # Cleanup
        measurement.close_plots()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()
