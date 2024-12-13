# README: Traffic Simulation Plots

This simulation compares the impact of Adaptive Cruise Control (ACC) vehicles vs. Human-Driven vehicles on a road. Each plot helps visualize different aspects of traffic flow, congestion, and driver behavior.

**Simulation Parameters:**
- **L:** Road length (number of cells).
- **N:** Number of cars on the road.
- **vmax:** Maximum vehicle speed (in cells/step).
- **p_fault:** Probability of random slowdowns.
- **p_slow:** Probability of slow-to-start behavior.
- **rho (traffic density):** Defined as N/L, indicating how "full" the road is.

All these parameters are included in the titles of the plots for reference.

---

## 1. Velocity Distribution
**What:** Shows a histogram of car velocities at the end of the simulation.  
**Why:** To compare how often ACC cars vs. Non-ACC cars reach certain speeds.  
**How:** At the end of the simulation, we record each car’s final velocity. We then bin these values into a histogram.  
**Code:** Uses arrays of velocities from `cars_road1` (ACC) and `cars_road2` (No ACC) and `plt.hist()` to produce the plot.

---

## 2. Velocity Distribution with Parameters (p_fault, p_slow)
**What:** Shows how changing `p_fault` and `p_slow` affects the velocity distribution of Non-ACC cars.  
**Why:** To understand the sensitivity of human-like behavior parameters on traffic performance.  
**How:** Run multiple simulations, store velocities for different `(p_fault, p_slow)` pairs, then plot histograms for each scenario.  
**Code:** A dictionary indexed by `(p_fault, p_slow)` is used. For each key, a histogram is generated.

---

## 3. Flow Rate Over Time
**What:** Plots the average speed (used as a proxy for flow rate) of ACC vs. Non-ACC cars over time.  
**Why:** To see if ACC stabilizes flow and maintains higher average speeds.  
**How:** Each step, we compute the mean velocity of all cars on each road. Over time, this forms a time-series that indicates traffic flow.  
**Code:** Uses `flow_rate_acc` and `flow_rate_no_acc` arrays recorded each timestep and `plt.plot()` to show the evolution.

---

## 4. Additional Metrics (Jam Length & Stops Distribution)
**What:** Two sets of plots:
- **Jam Length Over Time:** How long congested (stopped) segments persist.
- **Stops Distribution:** How many times each car stops during the simulation.  
**Why:** To identify how ACC might reduce the formation or severity of jams and reduce the frequency of stops.  
**How:** We identify stopped cells to compute jam length each step and record the total stops per car at the end of the simulation.  
**Code:** `jam_lengths_acc` and `jam_lengths_no_acc` are updated each step. `stops_acc` and `stops_no_acc` are final counts. `plt.plot()` for jam lengths, `plt.hist()` for stops.

---

## 5. Fraction of Stopped Cars Over Time
**What:** Shows what fraction of cars are stopped at each timestep.  
**Why:** To track how often and how severely traffic breaks down.  
**How:** Each timestep, count how many cars have velocity == 0, divide by N. This fraction is recorded and plotted over time.  
**Code:** Uses `fraction_stopped_road1` and `fraction_stopped_road2` arrays updated every simulation step and `plt.plot()` them.

---

## 6. Delay Over Time
**What:** Plots the average delay (%) of ACC vs. Non-ACC cars over time. Delay is defined as `(vmax - avg_speed)/vmax * 100`.  
**Why:** To evaluate how congestion affects travel times. Higher delay means cars are going slower compared to their maximum possible speed.  
**How:** At each timestep, compute average speed and derive delay. Store in `delay_acc` and `delay_no_acc`. Plot these over time.  
**Code:** Computed each step from `average_speed`. `plt.plot()` is used to visualize.

---

## 7. Stop-Start Frequency Distribution
**What:** A histogram of how many times each car transitions from moving to stopped or stopped to moving.  
**Why:** Frequent stop-start cycles indicate unstable traffic flow. ACC might reduce these oscillations.  
**How:** For each car, track velocity changes each step. When velocity crosses from >0 to 0 or 0 to >0, increment a counter. At the end, plot these frequencies.  
**Code:** Uses `stop_start_acc` and `stop_start_no_acc` arrays built from per-car counters and `plt.hist()` to present the distribution.

---

## 8. Distance Traveled Distribution
**What:** Shows the distribution of total distance traveled by individual cars on both ACC and Non-ACC roads.

**Why:** To compare the efficiency and effectiveness of ACC in maintaining traffic flow and reducing unnecessary stops or delays. By analyzing how much distance each car covers, we can assess whether ACC cars are able to travel farther and more consistently than their Non-ACC counterparts.

**How:** At the end of the simulation, the total distance traveled by each car is recorded. These distances are then visualized using seaborn's Kernel Density Estimation (KDE) plots to illustrate the distribution for both ACC and Non-ACC cars. This allows for a clear comparison of the performance between the two groups.

**Code:** Utilizes distances_acc and distances_no_acc arrays from cars_road1 (ACC) and cars_road2 (Non-ACC) respectively. Seaborn's sns.kdeplot() is employed to generate density plots, which are saved as images for further analysis.



---

## 9. Velocity CDF (Cumulative Distribution Function)
**What:** Plots the CDF of final velocities for ACC and Non-ACC cars.  
**Why:** A CDF shows the probability of a car being at or below a certain speed. It provides insight into overall speed profile stability.  
**How:** Sort the velocities, compute a cumulative count ratio (i.e., `np.arange(1, len(v)+1)/len(v)`), and plot as a CDF.  
**Code:** Sort arrays `velocities_acc` and `velocities_no_acc`. Use `np.arange()` to compute cumulative probabilities and `plt.plot()`.
