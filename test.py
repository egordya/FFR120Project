import numpy as np
from Car import Car

def test_speed_offset_distribution(num_cars=1000):
    """
    Test the distribution of speed_offset assignments in the Car class.

    Parameters:
        num_cars (int): Number of cars to initialize and test.
    """
    faster_count = 0
    slower_count = 0
    normal_count = 0

    for _ in range(num_cars):
        car = Car(
            road_length=100,
            cell_width=1,
            max_speed=5,
            p_fault=0.1,
            p_slow=0.1,
            adaptive_cruise_control=False
        )
        if car.speed_offset > 0:
            faster_count += 1
        elif car.speed_offset < 0:
            slower_count += 1
        else:
            normal_count += 1

    print(f"Out of {num_cars} cars:")
    print(f"Faster: {faster_count} ({(faster_count / num_cars) * 100:.2f}%)")
    print(f"Slower: {slower_count} ({(slower_count / num_cars) * 100:.2f}%)")
    print(f"Normal: {normal_count} ({(normal_count / num_cars) * 100:.2f}%)")

def test_multiple_runs(num_cars=30, num_runs=10):
    """
    Perform multiple runs of speed_offset distribution tests with a small sample size.

    Parameters:
        num_cars (int): Number of cars per run.
        num_runs (int): Number of runs to perform.
    """
    for run in range(1, num_runs + 1):
        faster_count = 0
        slower_count = 0
        normal_count = 0

        for _ in range(num_cars):
            car = Car(
                road_length=100,
                cell_width=1,
                max_speed=5,
                p_fault=0.1,
                p_slow=0.1,
                adaptive_cruise_control=False
            )
            if car.speed_offset > 0:
                faster_count += 1
            elif car.speed_offset < 0:
                slower_count += 1
            else:
                normal_count += 1

        print(f"Run {run}:")
        print(f"Faster: {faster_count} ({(faster_count / num_cars) * 100:.2f}%)")
        print(f"Slower: {slower_count} ({(slower_count / num_cars) * 100:.2f}%)")
        print(f"Normal: {normal_count} ({(normal_count / num_cars) * 100:.2f}%)\n")

if __name__ == "__main__":
    # Example 1: Single large run
    print("Single Large Run (1000 Cars):")
    test_speed_offset_distribution(num_cars=1000)
    print("\n" + "-"*50 + "\n")

    # Example 2: Multiple small runs
    print("Multiple Small Runs (30 Cars each, 10 Runs):")
    test_multiple_runs(num_cars=30, num_runs=10)
