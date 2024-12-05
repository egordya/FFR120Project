import pygame
import numpy as np

class Car:
    def __init__(self, road_length, cell_width, max_speed, p_fault, p_slow, position=None, velocity=0,
                 color=(0, 255, 0), cruise_control=False):
        """
        Initialize a Car instance.

        :param road_length: Total number of cells on the road.
        :param cell_width: Width of each cell in pixels.
        :param max_speed: Maximum speed (vmax) of the car.
        :param p_fault: Probability of random slowdown (pfault).
        :param p_slow: Probability of slow-to-start (pslow).
        :param position: Initial position (cell index). If None, randomly assign.
        :param velocity: Initial velocity. Defaults to 0.
        :param color: Initial color. Defaults to green.
        :param cruise_control: Boolean flag indicating if Cruise Control is active.
        """
        self.road_length = road_length
        self.cell_width = cell_width
        self.max_speed = max_speed
        self.p_fault = p_fault
        self.p_slow = p_slow
        self.position = position if position is not None else np.random.randint(0, road_length)
        self.velocity = velocity
        self.color = color

        # Additional Metrics
        self.total_distance = 0
        self.stops = 0
        self.time_in_traffic = 0

        # Slow-to-Start flag
        self.slow_to_start = False  # Indicates if the car is in the 'slow-to-start' state

        # Cruise Control flag
        self.cruise_control = cruise_control

    def update_velocity(self, distance_to_next_car, velocity_of_next_car):
        """
        Update the car's velocity based on the BJH model with 'slow-to-stop' rule and Cruise Control.

        :param distance_to_next_car: Number of empty cells ahead of the car.
        :param velocity_of_next_car: Velocity of the car immediately ahead.
        """
        # If Cruise Control is active, aim to maintain a set speed
        if self.cruise_control:
            desired_speed = self.max_speed-1  # You can set this to a different value if desired
            if self.velocity < desired_speed and distance_to_next_car > self.velocity:
                self.velocity += 1  # Accelerate to desired speed
            elif self.velocity > desired_speed:
                self.velocity -= 1  # Decelerate to desired speed
            # Ensure the car does not exceed the desired speed
            self.velocity = min(self.velocity, desired_speed)

        # Rule 1: Slow-to-Start
        if self.velocity == 0:
            if distance_to_next_car > 1:
                if self.slow_to_start:
                    # Previously decided to stay stopped; now accelerate to 1
                    self.velocity = 1
                    self.slow_to_start = False
                else:
                    # Decide whether to stay stopped or start moving
                    if np.random.rand() < self.p_slow:
                        # Stay stopped this time step; accelerate next step
                        self.slow_to_start = True
                        self.velocity = 0
                    else:
                        # Accelerate normally
                        self.velocity = 1
                        self.slow_to_start = False
            else:
                # Too close to accelerate; stay stopped
                self.velocity = 0
                self.slow_to_start = False

        else:
            # Rule 2: Deceleration when the next car is near or slowing down
            if distance_to_next_car <= self.velocity:
                if self.velocity < velocity_of_next_car or self.velocity <= 2:
                    self.velocity = distance_to_next_car - 1
                elif self.velocity >= velocity_of_next_car and self.velocity > 2:
                    self.velocity = min(distance_to_next_car - 1, self.velocity - 2)

            # Rule 3: Deceleration when the next car is farther but within 2v
            elif self.velocity < distance_to_next_car <= 2 * self.velocity:
                if self.velocity >= velocity_of_next_car + 4:
                    self.velocity = max(self.velocity - 2, 0)
                elif velocity_of_next_car + 2 <= self.velocity <= velocity_of_next_car + 3:
                    self.velocity = max(self.velocity - 1, 0)

            # Rule 4: Acceleration
            if self.velocity < self.max_speed and distance_to_next_car > self.velocity + 1:
                self.velocity += 1

            # Rule 5: Randomization
            if self.velocity > 0 and np.random.rand() < self.p_fault:
                self.velocity = max(self.velocity - 1, 0)

    def move(self):
        """
        Move the car forward based on its velocity.
        """
        self.position = (self.position + self.velocity) % self.road_length
        self.total_distance += self.velocity
        if self.velocity == 0:
            self.stops += 1
        self.time_in_traffic += 1

    def draw(self, screen, road_y, car_height):
        """
        Render the car on the Pygame window with a direction indicator.

        :param screen: Pygame display surface.
        :param road_y: Y-coordinate of the road center.
        :param car_height: Height of the car rectangle in pixels.
        """
        x = self.position * self.cell_width + (self.cell_width * 0.1)
        y = road_y - car_height // 2

        # Determine color based on speed
        if self.velocity == 0:
            color = (255, 0, 0)  # Red
        elif self.velocity < self.max_speed / 2:
            # Gradient from red to yellow
            gradient_value = int(255 * (self.velocity / (self.max_speed / 2)))
            # Ensure gradient_value is within 0-255
            gradient_value = max(0, min(gradient_value, 255))
            color = (255, gradient_value, 0)
        else:
            color = (0, 255, 0)  # Green

        # If Cruise Control is active, override color to blue
        if self.cruise_control:
            color = (0, 0, 255)  # Blue

        # Validate color tuple
        if not (isinstance(color, tuple) and len(color) == 3 and all(isinstance(c, int) and 0 <= c <= 255 for c in color)):
            print(f"Invalid color detected: {color} for car at position {self.position}")
            color = (0, 0, 0)  # Default to black to prevent crashing

        # Draw the car as a rectangle
        pygame.draw.rect(screen, color, (x, y, self.cell_width * 0.8, car_height))

        # Draw direction indicator (arrowhead)
        arrow_size = 5  # Size of the arrowhead
        arrow_color = (0, 0, 0)  # Black

        # Determine the direction based on velocity
        if self.velocity > 0:
            # Arrow pointing to the right
            point1 = (x + self.cell_width * 0.8, y + car_height // 2)
            point2 = (x + self.cell_width * 0.8 - arrow_size, y + car_height // 2 - arrow_size)
            point3 = (x + self.cell_width * 0.8 - arrow_size, y + car_height // 2 + arrow_size)
        else:
            # Arrow pointing to the left (for stopped cars)
            point1 = (x, y + car_height // 2)
            point2 = (x + arrow_size, y + car_height // 2 - arrow_size)
            point3 = (x + arrow_size, y + car_height // 2 + arrow_size)

        pygame.draw.polygon(screen, arrow_color, [point1, point2, point3])

    def toggle_cruise_control(self):
        """
        Toggle the Cruise Control status of the car.
        """
        self.cruise_control = not self.cruise_control
