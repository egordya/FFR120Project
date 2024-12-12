import pygame
import numpy as np

class Car:
    def __init__(self, road_length, cell_width, max_speed, p_fault, p_slow, position=None, velocity=0,
                 color=(0, 255, 0), adaptive_cruise_control=False):
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

        if not self.adaptive_cruise_control:
            # Offset logic for Road 2 (as in the original code)
            random_value = np.random.rand()
            if random_value < 0.50:  # 5% faster
                self.speed_offset = np.random.randint(1, 3)  # +1 or +2
            elif random_value < 0.50:  # next 15% slower (Note: This condition is never reached as is,
                                       # but we keep the original logic that you provided)
                self.speed_offset = -np.random.randint(1, 3)  # -1 or -2
            else:  # 80% no offset
                self.speed_offset = 0
        else:
            # ACC cars have no speed offset
            self.speed_offset = 0

            # PID controller variables for ACC
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

        if self.adaptive_cruise_control:
            # Adaptive Cruise Control Parameters
            safe_time_headway = 2.0
            standstill_distance = 1.0
            w_speed = 0.5
            kp = 0.5
            ki = 0.0
            kd = 0.2
            """
            PID Controller Parameters:

            kp (Proportional Gain):
                - Controls the reaction to the current error.
                - Increasing kp makes the controller respond more aggressively to errors.
                - If kp is too high, the system may become unstable and oscillate.
                - If kp is too low, the system may respond sluggishly.
                - Suggested Interval: 0.1 to 1.0

            ki (Integral Gain):
                - Controls the reaction based on the accumulation of past errors.
                - Increasing ki helps eliminate steady-state errors.
                - If ki is too high, it can lead to overshooting and oscillations.
                - If ki is too low, steady-state errors may persist.
                - Suggested Interval: 0.0 to 0.5

            kd (Derivative Gain):
                - Controls the reaction based on the rate of change of the error.
                - Increasing kd helps dampen the system and reduce overshoot.
                - If kd is too high, it can amplify noise and cause instability.
                - If kd is too low, the system may overshoot more.
                - Suggested Interval: 0.0 to 0.5
            """
            detection_range = 50
            lead_car_detected = (detection_range > distance_to_next_car > 0)

            if lead_car_detected:
                desired_gap = standstill_distance + self.velocity * safe_time_headway
                error_distance = desired_gap - distance_to_next_car
                error_speed = velocity_of_next_car - self.velocity
                combined_error = error_distance + w_speed * error_speed
            else:
                # No lead car: just maintain target speed
                combined_error = self.target_speed - self.velocity

            # PID calculation as before...
            self.integral_error += combined_error
            derivative_error = combined_error - self.last_error
            self.last_error = combined_error

            acceleration_change = kp * combined_error + ki * self.integral_error + kd * derivative_error

            threshold = 0.5
            if acceleration_change > threshold:
                self.velocity = max(self.velocity - 1, 0)
            elif acceleration_change < -threshold and self.velocity < self.target_speed:
                self.velocity = min(self.velocity + 1, self.target_speed)

            # Reduce random slowdowns drastically for ACC
            effective_p_fault = self.p_fault * 0.01
            if self.velocity > 0 and np.random.rand() < effective_p_fault:
                self.velocity = max(self.velocity - 1, 0)


        else:
            # Road 2 logic (unchanged)
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
