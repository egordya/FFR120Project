# run_simulation.py

import sys
import numpy as np
import matplotlib

matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt

from Car import Car
from MeasurementAndPlotter import MeasurementAndPlotter


def run_simulation(headless=False):
    # Simulation Parameters
    L = 120  # Road length
    N = 30   # Number of cars per road
    vmax = 4  # Maximum speed
    p_fault = 0.1  # Probability of random slowdown
    p_slow = 0.5  # Probability of slow-to-start behavior
    steps = 5000  # Number of steps
    DRAW_GRID = True
    rho = N / L  # Traffic density

    prob_faster = 0.40
    prob_slower = 0.10
    prob_normal = 0.50

    # Validate that probabilities sum to 1
    if not np.isclose(prob_faster + prob_slower + prob_normal, 1.0):
        raise ValueError("prob_faster, prob_slower, and prob_normal must sum to 1.")

    SIM_STEPS_PER_SECOND = 20
    SIMULATION_STEP_INTERVAL = 1000 / SIM_STEPS_PER_SECOND
    cruise_control_percentage_road1 = 100

    N_ACC_CARS = int(cruise_control_percentage_road1 / 100 * N)

    # Initialize simulation_data with new arrays
    simulation_data = {
        'time_steps': [],
        'flow_rate_acc': [],
        'flow_rate_no_acc': [],
        'jam_lengths_acc': [],
        'jam_lengths_no_acc': [],
        'fraction_stopped_road1': [],
        'fraction_stopped_road2': [],
        'delay_acc': [],
        'delay_no_acc': [],
        'prob_faster': prob_faster,
        'prob_slower': prob_slower,
        'prob_normal': prob_normal,
        'p_fault': p_fault,
        'p_slow': p_slow,
        'N': N,
        'L': L,
        'vmax': vmax,
        'rho': rho
    }

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
        DODGERBLUE = (30, 144, 255)
        SALMON = (250, 128, 114)

        ROAD_Y_TOP = WINDOW_HEIGHT // 3
        ROAD_Y_BOTTOM = 2 * WINDOW_HEIGHT // 3
        CELL_WIDTH = WINDOW_WIDTH / L
        CAR_HEIGHT = 20
    else:
        WHITE = BLACK = DODGERBLUE = SALMON = None
        CELL_WIDTH = 1
        CAR_HEIGHT = 1
        ROAD_Y_TOP = ROAD_Y_BOTTOM = None

    # Initialize Roads
    occupied_positions_road1 = set()
    cars_road1 = []
    for _ in range(N):
        position = np.random.randint(0, L)
        while position in occupied_positions_road1:
            position = np.random.randint(0, L)
        occupied_positions_road1.add(position)
        acc_enabled = (np.random.rand() < (cruise_control_percentage_road1 / 100))
        car = Car(
            road_length=L,
            cell_width=CELL_WIDTH,
            max_speed=vmax,
            p_fault=p_fault,
            p_slow=p_slow,
            prob_faster=prob_faster,
            prob_slower=prob_slower,
            prob_normal=prob_normal,
            position=position,
            adaptive_cruise_control=acc_enabled
        )
        cars_road1.append(car)

    occupied_positions_road2 = set()
    cars_road2 = []
    for _ in range(N):
        position = np.random.randint(0, L)
        while position in occupied_positions_road2:
            position = np.random.randint(0, L)
        occupied_positions_road2.add(position)
        car = Car(
            road_length=L,
            cell_width=CELL_WIDTH,
            max_speed=vmax,
            p_fault=p_fault,
            p_slow=p_slow,
            prob_faster=prob_faster,
            prob_slower=prob_slower,
            prob_normal=prob_normal,
            position=position,
            adaptive_cruise_control=False
        )
        cars_road2.append(car)

    highlight_car_road1 = cars_road1[0] if cars_road1 else None
    highlight_car_road2 = cars_road2[0] if cars_road2 else None

    paused = False
    running = True
    step = 0

    # For stop-start frequency tracking
    prev_velocity_road1 = {}
    prev_velocity_road2 = {}
    stop_start_count_road1 = {}
    stop_start_count_road2 = {}

    for c in cars_road1:
        prev_velocity_road1[c] = c.velocity
        stop_start_count_road1[c] = 0

    for c in cars_road2:
        prev_velocity_road2[c] = c.velocity
        stop_start_count_road2[c] = 0

    enable_flow_delay_plot = False
    enable_cars_stopped_plot = False
    enable_density_occupancy_plot = False
    enable_jam_queue_plot = False

    measurement = MeasurementAndPlotter(
        N, L, vmax,
        enable_flow_delay_plot=enable_flow_delay_plot,
        enable_cars_stopped_plot=enable_cars_stopped_plot,
        enable_density_occupancy_plot=enable_density_occupancy_plot,
        enable_jam_queue_plot=enable_jam_queue_plot,
        enable_fuel_consumption_plot=True
    )

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
                        clock.tick(FPS)
                        continue
                    else:
                        clock.tick(FPS)
                        continue
                else:
                    last_simulation_step_time = current_time

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

            # Compute metrics
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

            delay_road1 = (vmax - average_speed_road1) / vmax * 100 if vmax != 0 else 0
            delay_road2 = (vmax - average_speed_road2) / vmax * 100 if vmax != 0 else 0

            jam_length_road1, queue_duration_road1 = compute_jam_length_and_queue_duration(
                L, cars_road1, queue_duration_road1)
            jam_length_road2, queue_duration_road2 = compute_jam_length_and_queue_duration(
                L, cars_road2, queue_duration_road2)

            simulation_data['time_steps'].append(step)
            simulation_data['flow_rate_acc'].append(average_speed_road1)
            simulation_data['flow_rate_no_acc'].append(average_speed_road2)
            simulation_data['jam_lengths_acc'].append(queue_duration_road1)
            simulation_data['jam_lengths_no_acc'].append(queue_duration_road2)
            simulation_data['fraction_stopped_road1'].append(stopped_vehicles_road1 / N)
            simulation_data['fraction_stopped_road2'].append(stopped_vehicles_road2 / N)
            simulation_data['delay_acc'].append(delay_road1)
            simulation_data['delay_no_acc'].append(delay_road2)

            # Track stop-start transitions
            for car in cars_road1:
                if (prev_velocity_road1[car] == 0 and car.velocity > 0) or (
                        prev_velocity_road1[car] > 0 and car.velocity == 0):
                    stop_start_count_road1[car] += 1
                prev_velocity_road1[car] = car.velocity

            for car in cars_road2:
                if (prev_velocity_road2[car] == 0 and car.velocity > 0) or (
                        prev_velocity_road2[car] > 0 and car.velocity == 0):
                    stop_start_count_road2[car] += 1
                prev_velocity_road2[car] = car.velocity

            measurement.update_flow_delay_metrics(step, average_speed_road1, average_speed_road2, delay_road1,
                                                  delay_road2)
            measurement.update_cars_stopped_metrics(step, stopped_vehicles_road1, stopped_vehicles_road2)

            # Compute metrics again after updating
            average_speed_road1 = np.mean([c.velocity for c in cars_road1]) if cars_road1 else 0
            stopped_vehicles_road1 = sum(c.velocity == 0 for c in cars_road1)
            average_speed_road2 = np.mean([c.velocity for c in cars_road2]) if cars_road2 else 0
            stopped_vehicles_road2 = sum(c.velocity == 0 for c in cars_road2)

            delay_road1 = (vmax - average_speed_road1) / vmax * 100 if vmax != 0 else 0
            delay_road2 = (vmax - average_speed_road2) / vmax * 100 if vmax != 0 else 0

            jam_length_road1, queue_duration_road1 = compute_jam_length_and_queue_duration(
                L, cars_road1, queue_duration_road1)
            jam_length_road2, queue_duration_road2 = compute_jam_length_and_queue_duration(
                L, cars_road2, queue_duration_road2)

            # Update the plots that already worked
            measurement.update_flow_delay_metrics(step, average_speed_road1, average_speed_road2, delay_road1,
                                                  delay_road2)
            measurement.update_cars_stopped_metrics(step, stopped_vehicles_road1, stopped_vehicles_road2)

            # Update density/occupancy
            density_r1 = len(cars_road1) / L
            occupancy_r1_val = (len(set(c.position for c in cars_road1)) / L) * 100
            density_r2 = len(cars_road2) / L
            occupancy_r2_val = (len(set(c.position for c in cars_road2)) / L) * 100
            measurement.update_density_occupancy(step, density_r1, occupancy_r1_val, density_r2, occupancy_r2_val)

            # Update jam/queue
            measurement.update_jam_queue_metrics(step, jam_length_road1, jam_length_road2, queue_duration_road1,
                                                 queue_duration_road2)

            # Calculate velocities and accelerations for fuel consumption
            v_acc = np.mean([c.velocity for c in cars_road1 if c.adaptive_cruise_control])
            a_acc = np.mean([c.get_acceleration() for c in cars_road1 if c.adaptive_cruise_control])
            v_no_acc = np.mean([c.velocity for c in cars_road2])
            a_no_acc = np.mean([c.get_acceleration() for c in cars_road2])

            # Debugging output to verify input values
            print(f"Step: {step}, v_acc: {v_acc}, a_acc: {a_acc}, v_no_acc: {v_no_acc}, a_no_acc: {a_no_acc}")

            # Update fuel consumption metrics
            measurement.update_fuel_consumption_metrics(step, v_acc, a_acc, v_no_acc, a_no_acc)

            step += 1

            if not headless:
                screen.fill(WHITE)
                import pygame
                pygame.draw.line(screen, BLACK, (0, ROAD_Y_TOP), (2500, ROAD_Y_TOP), 2)
                pygame.draw.line(screen, BLACK, (0, ROAD_Y_BOTTOM), (2500, ROAD_Y_BOTTOM), 2)
                draw_grid(screen, ROAD_Y_TOP, L, CELL_WIDTH, WINDOW_HEIGHT=800, DRAW_GRID=DRAW_GRID)
                draw_grid(screen, ROAD_Y_BOTTOM, L, CELL_WIDTH, WINDOW_HEIGHT=800, DRAW_GRID=DRAW_GRID)

                for car in cars_road1:
                    car.draw(screen, ROAD_Y_TOP, CAR_HEIGHT, highlight=(car == highlight_car_road1))
                for car in cars_road2:
                    car.draw(screen, ROAD_Y_BOTTOM, CAR_HEIGHT, highlight=(car == highlight_car_road2))

                # Dynamic Text Rendering
                road1_text = f"Road 1 - {N_ACC_CARS} ACC Cars - Step: {step} | Avg Speed: {average_speed_road1:.2f} | Stopped: {stopped_vehicles_road1}"
                road1_surface = font.render(road1_text, True, DODGERBLUE)
                screen.blit(road1_surface, (20, 20))

                road2_text = f"Road 2 - {N} Human Drivers (No ACC) - Step: {step} | Avg Speed: {average_speed_road2:.2f} | Stopped: {stopped_vehicles_road2}"
                road2_surface = font.render(road2_text, True, SALMON)
                road2_text_x = 20
                road2_text_y = ROAD_Y_TOP + (ROAD_Y_BOTTOM - ROAD_Y_TOP) // 2
                screen.blit(road2_surface, (road2_text_x, road2_text_y))

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

        # Store stop-start frequency data in simulation_data
        simulation_data['stop_start_acc'] = [stop_start_count_road1[c] for c in cars_road1]
        simulation_data['stop_start_no_acc'] = [stop_start_count_road2[c] for c in cars_road2]

        # Plot results after simulation
        measurement.plot_results()

        return cars_road1, cars_road2, simulation_data


def draw_grid(screen, road_y, L, CELL_WIDTH, WINDOW_HEIGHT, DRAW_GRID):
    if DRAW_GRID:
        for i in range(L + 1):
            x = i * CELL_WIDTH
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


if __name__ == "__main__":
    run_simulation(headless=False)
