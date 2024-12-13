
# Car.py

import pygame
import numpy as np
import logging


class Car:
    # Define possible speed offsets
    SPEED_FAST = [1, 2]
    SPEED_SLOW = [-1, -2]
    SPEED_NORMAL = [0]

    def __init__(self, road_length, cell_width, max_speed, p_fault, p_slow,
                 prob_faster=0.20, prob_slower=0.10, prob_normal=0.70,
                 position=None, velocity=0, color=(0, 255, 0), adaptive_cruise_control=False):
        """
        Initialize a Car instance.

        Parameters:
            road_length (int): Length of the road.
            cell_width (int): Width of each cell on the road.
            max_speed (int): Maximum speed of the car.
            p_fault (float): Probability of a random slowdown (fault).
            p_slow (float): Probability of slow-to-start behavior.
            prob_faster (float, optional): Probability of the car being faster. Defaults to 0.20.
            prob_slower (float, optional): Probability of the car being slower. Defaults to 0.10.
            prob_normal (float, optional): Probability of the car driving normally. Defaults to 0.70.
            position (int, optional): Initial position of the car. Random if None.
            velocity (int, optional): Initial velocity of the car.
            color (tuple, optional): RGB color of the car.
            adaptive_cruise_control (bool, optional): Whether the car uses ACC.
        """
        self.road_length = road_length
        self.cell_width = cell_width
        self.max_speed = max_speed
        self.p_fault = p_fault
        self.p_slow = p_slow
        self.position = position if position is not None else np.random.randint(0, road_length)
        self.velocity = velocity
        self.color = color
        self.adaptive_cruise_control = adaptive_cruise_control

        self.total_distance = 0
        self.stops = 0
        self.time_in_traffic = 0
        self.slow_to_start = False

        # For ACC cars, target_speed = max_speed
        self.target_speed = self.max_speed

        # Assign speed offset based on probabilities
        if not self.adaptive_cruise_control:
            self.assign_speed_offset(prob_faster, prob_slower, prob_normal)
        else:
            # For Adaptive Cruise Control (ACC) cars, no speed offset
            self.speed_offset = 0

            # PID controller variables for ACC
            self.last_error = 0.0
            self.integral_error = 0.0

    def assign_speed_offset(self, prob_faster, prob_slower, prob_normal):
        """
        Assign a speed offset based on predefined probabilities.

        Parameters:
            prob_faster (float): Probability of the car being faster.
            prob_slower (float): Probability of the car being slower.
            prob_normal (float): Probability of the car driving normally.
        """
        categories = ['faster', 'slower', 'normal']
        probabilities = [prob_faster, prob_slower, prob_normal]

        # Validate probabilities
        if not np.isclose(sum(probabilities), 1.0):
            raise ValueError("Probabilities must sum to 1.")

        # Choose a category based on the defined probabilities
        category = np.random.choice(categories, p=probabilities)

        # Assign speed offset based on the chosen category
        if category == 'faster':
            self.speed_offset = np.random.choice(self.SPEED_FAST)
        elif category == 'slower':
            self.speed_offset = np.random.choice(self.SPEED_SLOW)
        else:
            self.speed_offset = 0



    def update_velocity(self, distance_to_next_car, velocity_of_next_car):
        # Slow-to-Start Logic (unchanged)
        if self.velocity == 0:
            if distance_to_next_car > 1:
                if self.slow_to_start:
                    self.velocity = 1
                    self.slow_to_start = False
                else:
                    if np.random.rand() < self.p_slow:
                        self.slow_to_start = True
                        self.velocity = 0
                    else:
                        self.velocity = 1
                        self.slow_to_start = False
            else:
                self.velocity = 0
                self.slow_to_start = False
            return  # Exit here if car was stopped

        if self.adaptive_cruise_control:
            # -------------------------------------
            # ACC Logic
            # -------------------------------------
            # Define parameters for the ACC-like behavior
            base_gap = 1
            time_headway = 1.5
            cruise_speed = self.max_speed  # target cruising speed in free flow
            desired_gap = base_gap + time_headway * self.velocity

            # Calculate the gap error
            gap_error = distance_to_next_car - desired_gap

            if distance_to_next_car < 2:
                # Extremely close - emergency deceleration
                self.velocity = max(distance_to_next_car - 1, 0)
            else:
                if gap_error < 0:
                    # Too close: decelerate
                    if self.velocity > velocity_of_next_car:
                        # Reduce speed to match or stay slightly behind the leading car
                        self.velocity = max(velocity_of_next_car, self.velocity - 1)
                    else:
                        # If we're already slower or equal to the next car but still too close, slow down more
                        self.velocity = max(self.velocity - 1, 0)
                else:
                    # We have more room than we need.
                    # Try to accelerate if below cruise speed and we have enough gap.
                    if self.velocity < cruise_speed and gap_error > 1:
                        self.velocity = self.velocity + 1
                    else:
                        # If near the desired gap, try to match speeds:
                        # If we're going faster and gap is small, slow a bit.
                        if self.velocity > velocity_of_next_car and gap_error < base_gap:
                            self.velocity = max(velocity_of_next_car, self.velocity - 1)
                        # If we're going slower and gap is large, speed up a bit.
                        elif self.velocity < velocity_of_next_car and gap_error > base_gap and self.velocity < cruise_speed:
                            self.velocity += 1
                        # Otherwise, maintain current speed if comfortable.

            # Randomization (Fault)
            if self.velocity > 0 and np.random.rand() < self.p_fault:
                self.velocity = max(self.velocity - 1, 0)

        else:
            # -------------------------------------
            # Original Road 2 Logic (unchanged)
            # -------------------------------------
            effective_max_speed = self.max_speed + self.speed_offset

            # Rule 2: Deceleration near next car
            if distance_to_next_car <= self.velocity:
                if self.velocity < velocity_of_next_car or self.velocity <= 2:
                    self.velocity = distance_to_next_car - 1
                elif self.velocity >= velocity_of_next_car and self.velocity > 2:
                    self.velocity = min(distance_to_next_car - 1, self.velocity - 2)

            # Rule 3: Deceleration if within 2v but not too close
            elif self.velocity < distance_to_next_car <= 2 * self.velocity:
                if self.velocity >= velocity_of_next_car + 4:
                    self.velocity = max(self.velocity - 2, 0)
                elif velocity_of_next_car + 2 <= self.velocity <= velocity_of_next_car + 3:
                    self.velocity = max(self.velocity - 1, 0)

            # Rule 4: Acceleration
            if self.velocity < effective_max_speed and distance_to_next_car > self.velocity + 1:
                self.velocity += 1

            # Rule 5: Randomization
            if self.velocity > 0:
                if np.random.rand() < self.p_fault:
                    self.velocity = max(self.velocity - 1, 0)

    def move(self):
        """
        Move the car based on its current velocity.
        """
        self.position = (self.position + self.velocity) % self.road_length
        self.total_distance += self.velocity
        if self.velocity == 0:
            self.stops += 1
        self.time_in_traffic += 1

    def draw(self, screen, road_y, car_height, highlight=False):
        """
        Draw the car on the pygame screen.

        Parameters:
            screen (pygame.Surface): The pygame screen surface.
            road_y (int): Y-coordinate of the road.
            car_height (int): Height of the car rectangle.
            highlight (bool, optional): Whether to highlight the car.
        """
        x = self.position * self.cell_width + (self.cell_width * 0.1)
        y = road_y - car_height // 2

        # Color based on speed
        if self.velocity == 0:
            self.color = (255, 0, 0)  # Red
        elif self.velocity < self.max_speed / 2:
            green_value = int(255 * (self.velocity / (self.max_speed / 2)))
            green_value = min(max(green_value, 0), 255)
            self.color = (255, green_value, 0)
        else:
            red_value = int(255 * (1 - (self.velocity - (self.max_speed / 2)) / (self.max_speed / 2)))
            red_value = min(max(red_value, 0), 255)
            self.color = (red_value, 255, 0)

        car_rect = pygame.Rect(x, y, self.cell_width * 0.8, car_height)
        pygame.draw.rect(screen, self.color, car_rect)

        # Outline for ACC cars
        if self.adaptive_cruise_control:
            outline_color = (0, 0, 255)  # Blue outline for ACC
            pygame.draw.rect(screen, outline_color, car_rect, 2)

        # Draw arrow indicating direction
        arrow_size = 5
        arrow_color = (0, 0, 0)

        if self.velocity > 0:
            point1 = (x + self.cell_width * 0.8, y + car_height // 2)
            point2 = (x + self.cell_width * 0.8 - arrow_size, y + car_height // 2 - arrow_size)
            point3 = (x + self.cell_width * 0.8 - arrow_size, y + car_height // 2 + arrow_size)
        else:
            point1 = (x, y + car_height // 2)
            point2 = (x + arrow_size, y + car_height // 2 - arrow_size)
            point3 = (x + arrow_size, y + car_height // 2 + arrow_size)

        pygame.draw.polygon(screen, arrow_color, [point1, point2, point3])

        # Draw highlight marker if needed
        if highlight:
            marker_radius = 5
            marker_color = (255, 0, 0)  # Red
            marker_x = x + (self.cell_width * 0.8) / 2
            marker_y = y - marker_radius - 2  # Positioned just above the car
            pygame.draw.circle(screen, marker_color, (int(marker_x), int(marker_y)), marker_radius)
