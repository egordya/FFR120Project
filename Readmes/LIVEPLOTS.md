# README: Live Traffic Simulation Plots

This simulation visualizes various aspects of traffic dynamics by comparing Adaptive Cruise Control (ACC) vehicles against Human-Driven vehicles (No ACC) on parallel roads. Live plots provide real-time insights into traffic flow, congestion, and driver behavior, enabling a comprehensive analysis of the simulation's performance.

**Simulation Parameters:**
- **L:** Road length (number of cells).
- **N:** Number of cars on each road.
- **vmax:** Maximum vehicle speed (in cells/step).
- **p_fault:** Probability of random slowdowns.
- **p_slow:** Probability of slow-to-start behavior.
- **rho (traffic density):** Defined as N/L, indicating how "full" the road is.

All these parameters are included in the titles of the plots for reference.

---

## 1. Flow and Delay Over Time
**What:**  
Displays the flow rate (cars per minute) and the average delay (%) for both ACC and Non-ACC cars over the simulation time.

**Why:**  
To monitor how traffic flow and vehicle delays evolve, allowing comparison between ACC-enabled vehicles and traditional human-driven vehicles. High flow rates with low delays indicate efficient traffic management, while discrepancies can highlight the benefits or drawbacks of ACC systems.

**How:**  
- **Flow Rate:** Calculated as the average speed of cars on each road per simulation step.
- **Average Delay:** Computed as the percentage difference between the maximum speed (`vmax`) and the average speed of cars.
- **Visualization:** Utilizes dual y-axes to plot both flow rate and average delay over time, with distinct line styles for ACC and Non-ACC cars.

**Code:**  
Uses `deque` structures to maintain a moving window of flow rates and delays, updating the plot in real-time with `plt.plot()`.

---

## 2. Number of Stopped Cars
**What:**  
Shows the number of cars that are stopped (velocity = 0) on each road in real-time.

**Why:**  
To assess the level of congestion and how often cars come to a complete stop. A higher number of stopped cars can indicate traffic jams or inefficiencies in traffic flow, whereas fewer stops suggest smoother traffic conditions.

**How:**  
- **Counting Stops:** Counts the number of cars with zero velocity on each road at each simulation step.
- **Visualization:** Represents the counts as bars for each road, updating their heights dynamically to reflect the current number of stopped cars.

**Code:**  
Employs `plt.bar()` to create and update bar charts, ensuring real-time feedback on congestion levels.

---

## 3. Density and Occupancy Over Time
**What:**  
Plots the density (vehicles per cell) and occupancy (%) for both ACC and Non-ACC cars over the simulation duration.

**Why:**  
- **Density:** Indicates how crowded the road is, which affects traffic flow and the likelihood of congestion.
- **Occupancy:** Reflects the percentage of road space occupied by vehicles, providing insights into traffic utilization and potential bottlenecks.

**How:**  
- **Density Calculation:** Number of cars divided by road length (`N/L`).
- **Occupancy Calculation:** Percentage of road cells occupied by cars.
- **Visualization:** Utilizes dual y-axes to plot density and occupancy, allowing simultaneous observation of both metrics for ACC and Non-ACC cars.

**Code:**  
Leverages `plt.plot()` for continuous lines representing density and occupancy, updating them in real-time using data from `deque` structures.

---

## 4. Jam Length and Queue Duration Over Time
**What:**  
Displays the length of traffic jams (in cells) and the duration of queues (in simulation steps) for both roads throughout the simulation.

**Why:**  
- **Jam Length:** Measures the spatial extent of traffic congestion, indicating how widespread a traffic jam is.
- **Queue Duration:** Tracks how long a traffic jam persists, providing insights into the stability of traffic flow and the effectiveness of ACC systems in alleviating congestion.

**How:**  
- **Jam Length Calculation:** Determines the longest consecutive sequence of stopped cars on each road.
- **Queue Duration Calculation:** Tracks how many consecutive simulation steps a traffic jam has been present.
- **Visualization:** Uses dual y-axes to plot both jam length and queue duration, with separate lines for each road to facilitate comparison.

**Code:**  
Implements `plt.plot()` for continuous tracking of jam metrics, updating the plot in real-time with data fed through `deque` structures.

---