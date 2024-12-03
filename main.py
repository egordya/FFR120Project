import pygame
import sys
import numpy as np
from Car import Car


def draw_grid(screen, road_y, L, CELL_WIDTH, WINDOW_HEIGHT, DRAW_GRID):
    if DRAW_GRID:
        # Draw vertical lines for each cell
        for i in range(L + 1):
            x = i * CELL_WIDTH
            # Draw lines spanning a portion of the window vertically
            pygame.draw.line(screen, (200, 200, 200), (x, road_y - WINDOW_HEIGHT // 4),
                             (x, road_y + WINDOW_HEIGHT // 4), 1)


def main():
    # Initialize Pygame
    pygame.init()

    # Simulation Parameters
    L = 100  # Length of the road (number of cells)
    N = 30  # Number of vehicles
    rho = N / L  # Traffic density
    vmax = 5  # Maximum speed
    p_fault = 0.1  # Probability of random slowdown (pfault)
    p_slow = 0.5  # Probability of slow-to-start (pslow)
    steps = 100000  # Number of simulation steps (set high for continuous simulation)
    DRAW_GRID = True  # Toggle grid visibility

    # Cruise Control Parameters
    cruise_control_count = 30  # Number of cars with Cruise Control enabled

    # Ensure cruise_control_count does not exceed the number of cars
    cruise_control_count = min(cruise_control_count, N)

    # Simulation Speed Parameters
    SIM_STEPS_PER_SECOND = 5  # Initial simulation steps per second
    last_simulation_step_time = pygame.time.get_ticks()

    # Pygame Window Dimensions
    WINDOW_WIDTH = 1600
    WINDOW_HEIGHT = 400
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("BJH Cellular Automaton Traffic Simulation with Cruise Control")

    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    YELLOW = (255, 255, 0)
    BLUE = (0, 0, 255)  # For Cruise Control cars

    # Road Visualization Parameters
    ROAD_Y = WINDOW_HEIGHT // 2
    CELL_WIDTH = WINDOW_WIDTH / L  # Width of each cell in pixels
    CAR_HEIGHT = 20

    # Initialize cars without overlapping
    occupied_positions = set()
    cars = []

    # Determine which cars will have Cruise Control
    cruise_control_indices = set(np.random.choice(N, cruise_control_count, replace=False))

    for i in range(N):
        position = np.random.randint(0, L)
        while position in occupied_positions:
            position = np.random.randint(0, L)
        occupied_positions.add(position)

        # Assign Cruise Control based on pre-selected indices
        cruise_control = i in cruise_control_indices

        # Ensure cruise_control is boolean
        cruise_control = bool(cruise_control)

        car = Car(
            road_length=L,
            cell_width=CELL_WIDTH,
            max_speed=vmax,
            p_fault=p_fault,
            p_slow=p_slow,
            position=position,
            velocity=np.random.randint(0, vmax + 1),  # Initialize with random velocity
            cruise_control=cruise_control
        )
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
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                mouse_x, mouse_y = event.pos
                for car in cars:
                    car_rect_x = car.position * CELL_WIDTH + (CELL_WIDTH * 0.1)
                    car_rect_y = ROAD_Y - CAR_HEIGHT // 2
                    car_rect = pygame.Rect(car_rect_x, car_rect_y, CELL_WIDTH * 0.8, CAR_HEIGHT)
                    if car_rect.collidepoint(mouse_x, mouse_y):
                        car.toggle_cruise_control()
                        break  # Toggle only one car per click

        # --- BJH Model Update Rules ---
        if not paused and current_time - last_simulation_step_time >= 1000 / SIM_STEPS_PER_SECOND:
            # Sort cars based on positions
            cars_sorted = sorted(cars, key=lambda car: car.position)

            # Calculate distances to the next car for each car
            for i, car in enumerate(cars_sorted):
                if i < len(cars_sorted) - 1:  # If not the last car
                    next_car = cars_sorted[i + 1]  # Next car
                    distance = next_car.position - car.position - 1  # Distance to the next car
                    if distance < 0:  # If the next car is behind
                        distance += L  # Wrap around for circular road
                else:
                    # Circular road: distance to the first car
                    next_car = cars_sorted[0]  # First car
                    distance = (next_car.position + L) - car.position - 1  # Distance to the first car
                velocity_of_next_car = next_car.velocity  # Velocity of the next car
                car.update_velocity(distance, velocity_of_next_car)  # Update the car's velocity

            # Move cars after updating velocities to prevent influence on distance calculations
            for car in cars_sorted:
                car.move()

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
            cruise_control_on = np.sum([car.cruise_control for car in cars])
            cruise_control_off = N - cruise_control_on
        else:
            average_speed = 0
            stopped_vehicles = 0
            cruise_control_on = 0
            cruise_control_off = 0

        # Render statistics text
        stats_text = (f"Step: {step} | Sim Steps/sec: {SIM_STEPS_PER_SECOND} | "
                      f"Avg Speed: {average_speed:.2f} | Stopped: {stopped_vehicles}")
        text_surface = font.render(stats_text, True, BLACK)
        screen.blit(text_surface, (10, 10))

        # Render Cruise Control statistics
        cc_text = (f"Cruise Control - ON: {cruise_control_on} | OFF: {cruise_control_off} "
                   f"(Click on a car to toggle)")
        cc_surface = font.render(cc_text, True, BLACK)
        screen.blit(cc_surface, (10, 30))

        # Render grid status
        grid_status = "ON" if DRAW_GRID else "OFF"
        grid_text = f"Grid: {grid_status} (Press 'G' to toggle)"
        grid_surface = font.render(grid_text, True, BLACK)
        screen.blit(grid_surface, (10, 50))

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
        cc_status = "ON" if car.cruise_control else "OFF"
        print(f"Car {idx + 1}:")
        print(f"  Cruise Control: {cc_status}")
        print(f"  Total Distance Traveled: {car.total_distance}")
        print(f"  Number of Stops: {car.stops}")
        print(f"  Time in Traffic: {car.time_in_traffic} steps\n")

    # Quit Pygame
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
