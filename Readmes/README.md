1. Slow-to-Start: As in the BJH rule, if v = 0 and d > 1 then with probability
1 − pslow the car accelerates normally (this step is ignored), and with probability pslow the car stays at velocity 0 on this time step (does not move)
and accelerates to v = 1 on the next time step.
2. Deceleration (when the next car is near): if d <= v and either v < vnext
or v <= 2, then the next car is either very close or going at a faster speed,
and we prevent a collision by setting v ← d − 1, but do not slow down more
than is necessary. Otherwise, if d <= v, v >= vnext , and v > 2 we set
v ← min(d − 1, v − 2) in order to possibly decelerate slightly more, since the
car ahead is slower or the same speed and the velocity of the current car is
substantial.
3. Deceleration (when the next car is farther): if v < d <= 2v, then if v >=
vnext +4, decelerate by 2 (v ← v−2). Otherwise, if vnext +2 <= v <= vnext +3
then decelerate by 1 (v ← v − 1).
4. Acceleration: if the speed has not been modiﬁed yet by one of rules 1-3 and
v < vmax and d > v + 1, then v ← v + 1.
5. Randomization: if v > 0, with probability pf ault , velocity decreases by one
(v ← v − 1).
6. Motion: the car advances v cells.

## Explanation:

Slow-to-Start
1. When a car is completely stopped and there's enough space ahead, it doesn't always start moving right away. 
Instead, there's a chance it decides to wait for one more moment before it begins to move.

2. **Deceleration (When the Next Car Is Near):**
If the car in front is very close or moving slower, the following car will slow down to avoid a crash. Specifically:

If the distance to the next car is less than or equal to the current car's speed, and either:
* The next car is going faster, or
* The current speed is low (2 or below),
then the following car reduces its speed just enough to stay safe.

3. Deceleration (When the Next Car Is Farther)
Even if the next car isn't immediately close, if it's somewhat far but within twice your speed, 
you might still need to slow down, especially if:

You're going much faster than the car ahead (by 4 or more),

Then: Slow down by 2 units of speed.

Or if you're going a bit faster than the car ahead (by 2 or 3),

Then: Slow down by 1 unit of speed.

4. **Acceleration**: If the speed has not been modified by one of rules 1-3 and `v < v_max` and `d > v + 1`, then set `v ← v + 1`.

    **Explanation:**
    - If none of the previous rules have altered the car's speed, and the current speed (`v`) is below the maximum allowed speed (`v_max`), and there is sufficient distance ahead (`d > v + 1`), the car accelerates by 1 unit (`v ← v + 1`).
    - This ensures that cars speed up to their maximum capacity when the road conditions permit, contributing to smoother traffic flow.

5. **Randomization**: If `v > 0`, with probability `p_fault`, the velocity decreases by one (`v ← v − 1`).

    **Explanation:**
    - To simulate real-world driver inattention or variability, there's a chance that a car will randomly slow down even if conditions allow it to maintain or increase speed.
    - With probability `p_fault`, a car that is moving (`v > 0`) reduces its speed by 1 unit, introducing unpredictability into the traffic flow and making the simulation more realistic.

6. **Motion**: The car advances `v` cells.

    **Explanation:**
    - After all speed adjustments have been made based on the above rules, the car moves forward by a number of cells equal to its current speed (`v`).
    - This final step updates the car's position on the road, reflecting its movement through the traffic simulation.

---

# Traffic Flow Simulation with Cruise Control Analysis

## Overview of the Simulation

### Objective
Simulate traffic flow to analyze the impact of cruise control on overall traffic dynamics.

### Tools Used
- **Python**: Core logic and computations.
- **Pygame**: Real-time visualization of the simulation.
- **Matplotlib**: Plotting traffic statistics such as flow rates and the number of stopped cars.

## Code Structure

### Car Class (`Car.py`)
**Purpose**: Represents individual vehicles in the simulation.

#### Key Attributes
- `position`: Current position of the car on the road.
- `velocity`: Current speed of the car.
- `max_speed`: Maximum allowable speed.
- `p_fault`: Probability that the driver will randomly slow down (simulating inattentiveness).
- `p_slow`: Probability of slow-to-start behavior after stopping.
- `cruise_control`: Boolean flag indicating whether the car has cruise control.

#### Key Methods
- `update_velocity()`: Updates the car's speed based on the BJH model rules and cruise control status.
- `move()`: Advances the car's position based on its velocity.
- `draw()`: Renders the car onto the Pygame window, including visual indicators.

### Main Simulation (`main.py`)
**Purpose**: Sets up the simulation environment, initializes vehicles, and runs the main simulation loop.

#### Key Components

##### Initialization
- Defines simulation parameters such as road length, number of cars, maximum speed, and probabilities.
- Creates two separate roads:
  - **Road 1**: Contains cars with cruise control.
  - **Road 2**: Contains cars without cruise control.

##### Main Loop
- Handles user inputs (pause, adjust speed, toggle grid).
- Updates car velocities and positions on both roads.
- Collects data for real-time plotting.
- Renders the simulation visuals.

##### Visualization
- **Pygame**: Displays the cars, roads, and simulation statistics.
- **Matplotlib**: Plots flow rates and the number of stopped cars over time for both roads.

## Implementation of the Cruise Control Feature

### Concept
Cruise control in the simulation represents cars that maintain a more consistent speed and are less prone to random slowdowns due to driver inattention. This reflects real-world cruise control systems that help drivers maintain set speeds.

### Implementation Details

#### Reduced Random Slowdown Probability
For cars with cruise control, the probability of random slowdown (`p_fault`) is reduced.

```python
if self.cruise_control:
    effective_p_fault = self.p_fault * 0.5  # Cruise control cars are less likely to slow down randomly
else:
    effective_p_fault = self.p_fault
```

This simulates the steadier speed maintenance of cruise control systems.

Preservation of 'Slow-to-Start' Behavior
Cruise control cars still experience the 'slow-to-start' rule, reflecting real-life scenarios where cruise control doesn't override traffic-induced delays.

Visual Indicators
Cars with cruise control are visually distinguished in the simulation for easy identification.

Simulation Mechanics
BJH Model Rules Applied
Rule 1: Slow-to-start behavior simulating driver hesitation when starting from a stop.
Rules 2 & 3: Deceleration rules based on the distance to the car ahead and its speed.
Rule 4: Acceleration up to the car's maximum speed when conditions allow.
Rule 5: Random slowdown to simulate driver inattention, with modifications for cruise control cars.
Car Updates
At each time step:

Cars calculate the distance to the next car and adjust their velocities accordingly.
Positions are updated based on the new velocities.
Data on flow rates and stopped cars are collected.
Visualization
Pygame Window: Displays two roads with moving cars and shows simulation statistics like average speed and the number of stopped cars.
Matplotlib Plots: Real-time graphs of flow rates and stopped cars for both roads, allowing comparison between roads with and without cruise control.
