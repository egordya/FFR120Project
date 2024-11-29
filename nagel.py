import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def initialize_road(length, density):
    """Initialize the road with cars placed randomly based on the given density."""
    road = [-1] * length
    for i in range(length):
        if random.random() < density:
            road[i] = random.randint(0, 5)  # Random initial speed between 0 and 5
    return road

def update_road(road, max_speed, prob_slowdown):
    """Update the road according to the Nagel-Schreckenberg rules."""
    length = len(road)
    new_road = [-1] * length
    flow_count = 0

    for i in range(length):
        if road[i] != -1:  # If there's a car at position i
            # Step 1: Acceleration
            speed = min(road[i] + 1, max_speed)

            # Step 2: Slowing down due to other cars
            distance = 1
            while distance <= speed and road[(i + distance) % length] == -1:
                distance += 1
            speed = min(speed, distance - 1)

            # Step 3: Randomization
            if random.random() < prob_slowdown:
                speed = max(speed - 1, 0)

            # Step 4: Car movement
            new_position = (i + speed) % length
            new_road[new_position] = speed

            # Count flow if car moves
            if speed > 0:
                flow_count += 1

    return new_road, flow_count

def simulate_traffic(length, density, max_speed, prob_slowdown, steps):
    """Simulate traffic for a given number of steps."""
    road = initialize_road(length, density)
    road_states = [road.copy()]
    flow_rates = []
    for _ in range(steps):
        road, flow_count = update_road(road, max_speed, prob_slowdown)
        road_states.append(road.copy())
        flow_rates.append(flow_count)
    return road_states, flow_rates

def animate_traffic(road_states, flow_rates, road_length, steps):
    """Animate the traffic simulation and plot density and flow rate."""
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8))
    
    # Traffic animation
    ax1.set_xlim(0, road_length)
    ax1.set_ylim(-1, 1)
    line, = ax1.plot([], [], 'bo', markersize=5)
    ax1.set_title('Traffic Simulation')

    # Density plot
    ax2.set_xlim(0, steps)
    ax2.set_ylim(0, 1)
    density_line, = ax2.plot([], [], 'r-')
    ax2.set_title('Vehicle Density (vehicles/km)')

    # Flow rate plot
    ax3.set_xlim(0, steps)
    ax3.set_ylim(0, max(flow_rates))
    flow_line, = ax3.plot([], [], 'g-')
    ax3.set_title('Flow Rate (vehicles/min)')

    def init():
        line.set_data([], [])
        density_line.set_data([], [])
        flow_line.set_data([], [])
        return line, density_line, flow_line

    def update(frame):
        # Update traffic animation
        x = [i for i, v in enumerate(road_states[frame]) if v != -1]
        y = [0] * len(x)
        line.set_data(x, y)

        # Update density plot
        density = sum(1 for v in road_states[frame] if v != -1) / road_length
        density_line.set_data(range(frame + 1), [sum(1 for v in road_states[i] if v != -1) / road_length for i in range(frame + 1)])

        # Update flow rate plot
        flow_line.set_data(range(frame + 1), flow_rates[:frame + 1])

        return line, density_line, flow_line

    ani = animation.FuncAnimation(fig, update, frames=steps,
                                  init_func=init, blit=True, interval=100)
    plt.tight_layout()
    plt.show()

# Parameters
road_length = 100
car_density = 0.3
max_speed = 5
probability_slowdown = 0.3
simulation_steps = 50

# Run simulation and animate
road_states, flow_rates = simulate_traffic(road_length, car_density, max_speed, probability_slowdown, simulation_steps)
animate_traffic(road_states, flow_rates, road_length, simulation_steps)
