# In Car.py

import pygame
import numpy as np


class Car:
    def __init__(self, road_length, cell_width, max_speed, p_fault, p_slow, position=None, velocity=0,
                 color=(0, 255, 0), cruise_control=False):
        self.road_length = road_length
        self.cell_width = cell_width
        self.max_speed = max_speed
        self.p_fault = p_fault
        self.p_slow = p_slow
        self.position = position if position is not None else np.random.randint(0, road_length)
        self.velocity = velocity
        self.color = color
        self.cruise_control = cruise_control

        self.total_distance = 0
        self.stops = 0
        self.time_in_traffic = 0
        self.slow_to_start = False

        # For cruise_control cars, target_speed = max_speed and we will use PID-like control
        self.target_speed = self.max_speed if self.cruise_control else self.max_speed

        if not self.cruise_control:
            # Offset logic for Road 2
            random_value = np.random.rand()
            if random_value < 0.50:  # 5% faster
                self.speed_offset = np.random.randint(1, 3)  # +1 or +2
            elif random_value < 0.50:  # next 15% slower
                self.speed_offset = -np.random.randint(1, 3)  # -1 or -2
            else:  # 80% no offset
                self.speed_offset = 0
        else:
            # Cruise control cars have no speed offset
            self.speed_offset = 0

            # PID controller variables for cruise control
            self.last_error = 0.0
            self.integral_error = 0.0

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

        if self.cruise_control:
            # Cruise Control with PID-like control

            # Parameters (tune these as needed)
            safe_time_headway = 2.0  # "seconds" (simulation steps) for desired time gap
            kp = 0.5  # Proportional gain
            ki = 0.0  # Integral gain (start with 0 for simplicity)
            kd = 0.2  # Derivative gain

            # Compute desired gap based on current velocity
            # Ensure a minimum gap of at least 2 cells
            desired_gap = max(2, self.velocity * safe_time_headway)

            # Error: positive error means we want a larger gap (too close), negative means too large a gap
            error = desired_gap - distance_to_next_car

            # Update PID terms
            self.integral_error += error
            derivative_error = error - self.last_error
            self.last_error = error

            # PID output for acceleration/deceleration
            # This will give a continuous value, which we translate to discrete velocity steps
            acceleration_change = kp * error + ki * self.integral_error + kd * derivative_error

            # Desired speed control:
            # If we have a large positive error (too close), we'll want to slow down
            # If negative error (too far), we can speed up (but not beyond self.target_speed)
            # We'll do small increments: ±1 cell per step for smoothness

            # Only adjust velocity if it's not at 0 after slow-to-start
            # If acceleration_change is large positive, we want to slow down more aggressively
            # If acceleration_change is large negative, we want to speed up
            threshold = 0.5  # threshold for deciding when to increment/decrement speed

            if acceleration_change > threshold:
                # Too close, slow down gently
                self.velocity = max(self.velocity - 1, 0)
            elif acceleration_change < -threshold and self.velocity < self.target_speed:
                # Too far, speed up gently
                self.velocity = min(self.velocity + 1, self.target_speed)

            # Reduce random slowdowns drastically for cruise control
            # We can either remove them or make them very rare
            effective_p_fault = self.p_fault * 0.01  # 1% of original fault probability
            if self.velocity > 0 and np.random.rand() < effective_p_fault:
                self.velocity = max(self.velocity - 1, 0)

        else:
            # Road 2 logic
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
        self.position = (self.position + self.velocity) % self.road_length
        self.total_distance += self.velocity
        if self.velocity == 0:
            self.stops += 1
        self.time_in_traffic += 1

    def draw(self, screen, road_y, car_height):
        x = self.position * self.cell_width + (self.cell_width * 0.1)
        y = road_y - car_height // 2

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

        # Draw outline for cruise control cars
        if self.cruise_control:
            outline_color = (0, 0, 255)  # Blue outline for cruise control
            pygame.draw.rect(screen, outline_color, car_rect, 2)

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
