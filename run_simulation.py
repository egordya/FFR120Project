# run_simulation.py



import sys
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

# Use a non-interactive backend for matplotlib when headless to avoid issues
# If you still have a display and want to see plots in non-headless mode, you can comment this line out.
matplotlib.use('Agg')
from HeadLessMeasurementAndPlotter import HeadLessMeasurementAndPlotter
plotter = HeadLessMeasurementAndPlotter(output_dir="plots")


# Import Car and MeasurementAndPlotter from your existing modules
from Car import Car
from MeasurementAndPlotter import MeasurementAndPlotter

def draw_grid(screen, road_y, L, CELL_WIDTH, WINDOW_HEIGHT, DRAW_GRID):
    if DRAW_GRID:
        for i in range(L + 1):
            x = i * CELL_WIDTH
            # Draw a vertical line representing the grid
            import pygame
            pygame.draw.line(screen, (200, 200, 200),
                             (x, road_y - WINDOW_HEIGHT // 8),
                             (x, road_y + WINDOW_HEIGHT // 8), 1)

def compute_jam_length_and_queue_duration(road_length, cars, previous_queue_duration):
    stopped = np.zeros(road_length, dtype=bool)
    for car in cars:
        if car.velocity == 0:
            stopped[car.position] = True

    max_run = 0
    current_run = 0
    for i in range(road_length):
        if stopped[i]:
            current_run += 1
            if current_run > max_run:
                max_run = current_run
        else:
            current_run = 0

    # Check wrap-around
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
    if max_run > 0:
        queue_duration = previous_queue_duration + 1
    else:
        queue_duration = 0

    return max_run, queue_duration

def run_simulation(headless=False):
    # Simulation Parameters
    L = 120
    N = 25
    vmax = 4
    p_fault = 0.1
    p_slow = 0.5
    steps = 10000
    DRAW_GRID = True

    SIM_STEPS_PER_SECOND = 20
    SIMULATION_STEP_INTERVAL = 1000 / SIM_STEPS_PER_SECOND

    cruise_control_percentage_road1 = 100

    # Setup Pygame if not headless
    if not headless:
        import pygame
        pygame.init()
        WINDOW_WIDTH = 2500
        WINDOW_HEIGHT = 800
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Traffic Simulation")
        font = pygame.font.SysFont(None, 24)
        clock = pygame.time.Clock()
        FPS = 60

        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        RED = (255, 0, 0)
        DODGERBLUE = (30, 144, 255)

        ROAD_Y_TOP = WINDOW_HEIGHT // 3
        ROAD_Y_BOTTOM = 2 * WINDOW_HEIGHT // 3
        CELL_WIDTH = WINDOW_WIDTH / L
        CAR_HEIGHT = 20
    else:
        # In headless mode, we do not initialize pygame or screen
        WHITE = BLACK = RED = DODGERBLUE = None
        CELL_WIDTH = 1  # Arbitrary, won't be rendered
        CAR_HEIGHT = 1
        ROAD_Y_TOP = ROAD_Y_BOTTOM = None
        # Just run as fast as possible, no event handling

    # Initialize Roads
    occupied_positions_road1 = set()
    cars_road1 = []
    for _ in range(N):
        position = np.random.randint(0, L)
        while position in occupied_positions_road1:
            position = np.random.randint(0, L)
        occupied_positions_road1.add(position)
        acc_enabled = (np.random.rand() < (cruise_control_percentage_road1 / 100))
        car = Car(road_length=L, cell_width=CELL_WIDTH, max_speed=vmax,
                  p_fault=p_fault, p_slow=p_slow,
                  position=position, adaptive_cruise_control=acc_enabled)
        cars_road1.append(car)

    occupied_positions_road2 = set()
    cars_road2 = []
    for _ in range(N):
        position = np.random.randint(0, L)
        while position in occupied_positions_road2:
            position = np.random.randint(0, L)
        occupied_positions_road2.add(position)
        car = Car(road_length=L, cell_width=CELL_WIDTH, max_speed=vmax,
                  p_fault=p_fault, p_slow=p_slow,
                  position=position, adaptive_cruise_control=False)
        cars_road2.append(car)

    highlight_car_road1 = cars_road1[0] if cars_road1 else None
    highlight_car_road2 = cars_road2[0] if cars_road2 else None

    paused = False
    running = True
    step = 0

    enable_main_plot = False
    enable_density_occupancy_plot = False
    enable_jam_queue_plot = False

    measurement = MeasurementAndPlotter(N, L,
                                        enable_main_plot=enable_main_plot,
                                        enable_density_occupancy_plot=enable_density_occupancy_plot,
                                        enable_jam_queue_plot=enable_jam_queue_plot)

    if not headless:
        import pygame
        last_simulation_step_time = pygame.time.get_ticks()
    else:
        last_simulation_step_time = 0

    queue_duration_road1 = 0
    queue_duration_road2 = 0

    try:
        while running and step < steps:
            if not headless:
                # Handle events and timing only in non-headless mode
                import pygame
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
                            DRAW_GRID = not DRAW_GRID
                        elif event.key == pygame.K_ESCAPE:
                            running = False

                control_message = measurement.check_control_messages()
                if control_message == "TERMINATE_FROM_PLOT":
                    running = False

                if paused or (current_time - last_simulation_step_time < SIMULATION_STEP_INTERVAL):
                    if paused:
                        # Just skip updating
                        clock.tick(FPS)
                        continue
                    else:
                        # Not enough time passed
                        clock.tick(FPS)
                        continue
                else:
                    # Update simulation step
                    last_simulation_step_time = current_time
            else:
                # Headless mode: run as fast as possible, no event handling, no timing
                pass

            # Update Road 1
            cars_sorted_road1 = sorted(cars_road1, key=lambda c: c.position)
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
            cars_sorted_road2 = sorted(cars_road2, key=lambda c: c.position)
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

            step += 1

            if not headless:
                # Rendering
                screen.fill(WHITE)
                import pygame
                pygame.draw.line(screen, BLACK, (0, ROAD_Y_TOP), (WINDOW_WIDTH, ROAD_Y_TOP), 2)
                pygame.draw.line(screen, BLACK, (0, ROAD_Y_BOTTOM), (WINDOW_WIDTH, ROAD_Y_BOTTOM), 2)
                draw_grid(screen, ROAD_Y_TOP, L, CELL_WIDTH, WINDOW_HEIGHT=800, DRAW_GRID=DRAW_GRID)
                draw_grid(screen, ROAD_Y_BOTTOM, L, CELL_WIDTH, WINDOW_HEIGHT=800, DRAW_GRID=DRAW_GRID)

                for car in cars_road1:
                    car.draw(screen, ROAD_Y_TOP, CAR_HEIGHT, highlight=(car == highlight_car_road1))
                for car in cars_road2:
                    car.draw(screen, ROAD_Y_BOTTOM, CAR_HEIGHT, highlight=(car == highlight_car_road2))

                if cars_road1:
                    average_speed_road1 = np.mean([c.velocity for c in cars_road1])
                    stopped_vehicles_road1 = np.sum([c.velocity == 0 for c in cars_road1])
                else:
                    average_speed_road1 = 0
                    stopped_vehicles_road1 = 0

                if cars_road2:
                    average_speed_road2 = np.mean([c.velocity for c in cars_road2])
                    stopped_vehicles_road2 = np.sum([c.velocity == 0 for c in cars_road2])
                else:
                    average_speed_road2 = 0
                    stopped_vehicles_road2 = 0

                stats_text_road1 = f"Road 1 - Step: {step} | Avg Speed: {average_speed_road1:.2f} | Stopped: {stopped_vehicles_road1}"
                text_surface_road1 = font.render(stats_text_road1, True, DODGERBLUE)
                screen.blit(text_surface_road1, (10, 10))

                stats_text_road2 = f"Road 2 - Step: {step} | Avg Speed: {average_speed_road2:.2f} | Stopped: {stopped_vehicles_road2}"
                text_surface_road2 = font.render(stats_text_road2, True, BLACK)
                screen.blit(text_surface_road2, (10, 400))

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
        running = False
        print("\nKeyboard Interrupt detected. Exiting...")
    finally:
        if not headless:
            measurement.close_plots()
            import pygame
            pygame.quit()

        # Print results
        print("\nSimulation Ended.\n")
        print("Road 1 Car Metrics:")
        for idx, car in enumerate(cars_road1):
            print(f"Car {idx + 1}: Total Distance: {car.total_distance}, Stops: {car.stops}, Time in Traffic: {car.time_in_traffic}")

        print("\nRoad 2 Car Metrics:")
        for idx, car in enumerate(cars_road2):
            print(f"Car {idx + 1}: Total Distance: {car.total_distance}, Stops: {car.stops}, Time in Traffic: {car.time_in_traffic}")

        if highlight_car_road1 and highlight_car_road2:
            distance_acc = highlight_car_road1.total_distance
            distance_non_acc = highlight_car_road2.total_distance
            relative_acc = distance_acc / vmax
            relative_non_acc = distance_non_acc / vmax
            print("\nComparison of Highlighted Cars:")
            print(f"ACC Car (Road 1): Distance={distance_acc}, Relative={relative_acc:.2f}")
            print(f"Non-ACC Car (Road 2): Distance={distance_non_acc}, Relative={relative_non_acc:.2f}")

            labels = ['ACC Car (Road 1)', 'Non-ACC Car (Road 2)']
            distances = [distance_acc, distance_non_acc]

            # In headless mode, save the plot to a file
            # In non-headless mode, you could show it interactively if you prefer.
            if headless:
                plt.figure(figsize=(6, 4))
                plt.bar(labels, distances, color=['blue', 'gray'])
                plt.ylabel('Total Distance Traveled (cells)')
                plt.title('Comparison of Highlighted Cars: ACC vs Non-ACC')
                plt.tight_layout()
                plt.savefig('comparison_plot.png')
                plt.close()
                print("Plot saved as 'comparison_plot.png'")
            else:
                # Show the plot interactively
                plt.figure(figsize=(6, 4))
                plt.bar(labels, distances, color=['blue', 'gray'])
                plt.ylabel('Total Distance Traveled (cells)')
                plt.title('Comparison of Highlighted Cars: ACC vs Non-ACC')
                plt.tight_layout()
                plt.show()

        return cars_road1, cars_road2

if __name__ == "__main__":
    # Run in normal mode with GUI
    run_simulation(headless=False)

    # Run in headless mode for fast execution
    # run_simulation(headless=True)
