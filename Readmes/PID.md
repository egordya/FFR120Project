Below is an updated, more organized explanation of the driving logic, separated into two sections: **Non-ACC Cars** and **ACC Cars**. Each section outlines the reasoning and the step-by-step rules that govern how the car's velocity is updated. The ACC logic differs from the original BJH steps to incorporate a PID controller for following the lead vehicle while maintaining a safer, more stable following distance and speed.

---

## Non-ACC Cars (Original BJH-Like Rules)

**Step-by-Step Logic:**

1. **Slow-to-Start:**
   - If `v = 0` and there is more than one cell of space ahead (`d > 1`):
     - With probability `1 - p_slow`: The car starts moving immediately (`v = 1`).
     - With probability `p_slow`: The car remains stopped for one more step and then starts moving (`v = 1`) on the next step.
   - If `d <= 1`, the car stays at `v = 0`.

   **Explanation:**
   This rule simulates a driver who may hesitate before starting, even when the road ahead is clear.

2. **Deceleration (When the Next Car Is Near):**
   - If the distance to the next car `d` is less than or equal to the car's current velocity `v` (`d <= v`):
     - If the next car is faster (`vnext > v`) or the current speed is 2 or below (`v <= 2`):
       - **Action:** Reduce speed just enough to avoid collision: `v ← d - 1`.
     - Otherwise, if the next car is slower or equal speed and current speed is above 2:
       - **Action:** Possibly decelerate more: `v ← min(d - 1, v - 2)`.

   **Explanation:**
   When the car gets too close to the car in front, it slows down to prevent a collision. Depending on how fast it’s going and how the car in front is moving, it may slow down minimally or a bit more aggressively.

3. **Deceleration (When the Next Car Is Farther):**
   - If `v < d <= 2v`, the next car is not too close but still within a range that might require adjustment:
     - If `v >= vnext + 4`, the car is much faster than the next car:
       - **Action:** Decelerate by 2: `v ← v - 2`.
     - Else if `vnext + 2 <= v <= vnext + 3`, the car is slightly faster than the next car:
       - **Action:** Decelerate by 1: `v ← v - 1`.

   **Explanation:**
   Even if not immediately near, the car anticipates the need to adjust speed if it’s approaching a slower car ahead. This makes the speed transitions smoother and avoids abrupt braking later.

4. **Acceleration:**
   - If none of the above rules changed the velocity, and `v < v_max` and `d > v + 1`:
     - **Action:** Accelerate by 1: `v ← v + 1`.

   **Explanation:**
   If the path is clear and the car is not at maximum speed, it speeds up gradually, promoting better traffic flow and reducing congestion.

5. **Randomization:**
   - If `v > 0`, with probability `p_fault`:
     - **Action:** Decrease velocity by 1: `v ← v - 1`.

   **Explanation:**
   This introduces an element of randomness, simulating human reaction times, distractions, or road irregularities that cause a car to slow down unexpectedly.

6. **Motion:**
   - After adjusting `v`, the car moves forward by `v` cells.

   **Explanation:**
   This updates the car’s position along the road after velocity changes have been applied.

---

## ACC Cars (Adaptive Cruise Control with PID)

**Step-by-Step Logic:**

1. **Slow-to-Start:**
   - ACC cars retain the same logic as above when starting from a standstill. If `v = 0`:
     - If `d > 1`:
       - With probability `1 - p_slow`, start moving (`v = 1`) immediately.
       - With probability `p_slow`, wait one step before moving (`v = 1` next step).
     - If `d <= 1`, stay at `v = 0`.

   **Explanation:**
   ACC-equipped cars still simulate human hesitation from a stop, though this could be adjusted if a perfectly computer-controlled start is desired.

2. **Adaptive Cruise Control (ACC) Using PID Control:**
   Once the car is moving (`v > 0`), the ACC logic replaces the BJH-type deceleration and acceleration rules. Instead of using fixed rules to adjust speed, the car employs a PID controller to maintain a safe following distance and speed.

   **Key Parameters:**
   - **Safe Time Headway:** The car aims to keep a time gap of about 2 simulation steps (`safe_time_headway = 2.0`) between it and the car ahead.
   - **Standstill Distance:** A desired standstill gap (1 cell) when stopped (`standstill_distance = 1.0`).
   - **Weight on Speed Error (`w_speed`):** A factor (0.5) that adjusts how much the difference in speed versus the car ahead influences the combined error.
   - **PID Gains:** `kp = 0.5`, `ki = 0.0`, `kd = 0.2` are chosen to provide a responsive yet stable control.

   **Process:**
   1. **Calculate Desired Gap:** `desired_gap = standstill_distance + v * safe_time_headway`.
      
      This sets a dynamic desired spacing that increases with speed, promoting smoother and safer driving at higher velocities.
   
   2. **Calculate Errors:**
      - **Distance Error:** `error_distance = desired_gap - d`.
      - **Speed Error:** `error_speed = vnext - v`.
      - **Combined Error:** `combined_error = error_distance + w_speed * error_speed`.
   
   3. **PID Computation:**
      - Update the integral term and compute the derivative of the error.
      - Compute the control output: 
        ```
        acceleration_change = kp * combined_error 
                            + ki * integral_error 
                            + kd * derivative_error
        ```
   
   4. **Adjust Velocity Based on PID Output:**
      - If `acceleration_change > threshold (0.5)`, the car is too close and should slow down: `v ← max(v - 1, 0)`.
      - If `acceleration_change < -threshold (-0.5)` and `v < target_speed`, the car should speed up: `v ← min(v + 1, target_speed)`.

   **Explanation:**
   Instead of strictly following a set of “if-then” deceleration and acceleration rules, the ACC car uses feedback (distance and relative speed) to the lead car to maintain a safe, stable headway. This approach more closely resembles modern adaptive cruise control systems in vehicles.

3. **Reduced Randomization:**
   - ACC cars are assumed to be more consistent and less prone to random slowdowns.
   - With probability `p_fault * 0.01`, decrease the velocity by 1.
   
   **Explanation:**
   ACC systems reduce driver-related variability, making random slowdowns significantly less frequent.

4. **Motion:**
   - After velocity adjustments, the ACC car moves forward by `v` cells.

   **Explanation:**
   As with non-ACC cars, this updates the car’s position on the road after the adjustments.

---

In summary, the **Non-ACC Cars** follow the original BJH rules (with modifications for slow-to-start and random fluctuations), applying step-by-step logic to decelerate or accelerate based on distance and relative speed. The **ACC Cars**, on the other hand, use a PID controller to dynamically adjust speed, aiming to maintain a target headway and smooth out the driving pattern, resulting in fewer abrupt changes and more stable traffic flow.


---

## Function: `assign_speed_offset`

### Description

The `assign_speed_offset` function is a method within the `Car` class responsible for assigning a speed offset to human-driven cars based on predefined probabilities. This variability makes the behavior of human drivers more **believable** by simulating realistic driving patterns such as speeding, slowing down, or maintaining a normal speed. For example if set like this:
   - prob_faster = 0.20
   - prob_slower = 0.10
   - prob_normal = 0.70

**Then under 20% of drivers will driver 1-2 vel. units faster, under 10% slower, and the rest will stick to vmax. Important to have the probabilities sum to 1.** 
### Purpose

Human drivers exhibit a range of behaviors influenced by various factors like attentiveness, road conditions, and personal driving habits. To mimic this diversity and enhance the realism of the simulation, the `assign_speed_offset` function introduces controlled randomness in the speed of human-driven cars.

### Parameters

- `prob_faster` (`float`):  
  The probability that the car will drive faster than its designated maximum speed.  
  **Range:** `0.0` to `1.0`

- `prob_slower` (`float`):  
  The probability that the car will drive slower than its designated maximum speed.  
  **Range:** `0.0` to `1.0`

- `prob_normal` (`float`):  
  The probability that the car will maintain its designated maximum speed without any offset.  
  **Range:** `0.0` to `1.0`