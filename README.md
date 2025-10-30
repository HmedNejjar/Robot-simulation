# Robot-simulation

This repository contains a basic Python-based simulator for managing a fleet of mobile robots on a 2D plane. The simulation includes functionalities for robot movement, battery consumption, and autonomous charging at designated stations.

## Features

*   **Robot Management**: Dynamically add or remove robots from the simulation.
*   **2D Movement**: Command robots to move from their current position to a new set of coordinates.
*   **Battery System**: Robots have a battery that depletes with movement. The consumption rate is proportional to the distance traveled.
*   **Charging Stations**: The simulation environment includes a predefined set of charging stations.
*   **Automated Charging**: Robots can be instructed to find the nearest available charging station and move to it to recharge.
*   **Autonomous Battery Management**: A background process monitors all robots and automatically sends them to charge when their battery level drops below a 20% threshold.
*   **Status Reporting**: View the real-time status of all robots—including name, ID, battery level, position, and charging state—in a clean `pandas` DataFrame.
*   **Concurrency**: Robot movement and charging actions are handled in separate threads to simulate simultaneous operations.

## Core Components

### `Robot.py`
This module defines the `Robot` class, which represents an individual robot in the simulation.

*   **Attributes**: Each robot has a unique `name`, `ID`, `position`, `_battery_lvl`, `_velocity`, and charging status (`_isCharging`).
*   **`move(dx, dy)`**: Simulates moving the robot by a delta `(dx, dy)`. This action takes time based on the robot's velocity and consumes the battery.
*   **`charge()`**: Initiates a background thread that gradually recharges the robot's battery.
*   **`stop_charging()`**: Halts the charging process.

### `RobotManager.py`
This module defines the `RobotManager` class, which oversees the entire fleet of robots and their interactions with the environment.

*   **`add_robot(name)`**: Creates and deploys a new robot at the origin `(0, 0)`.
*   **`del_robot(name)`**: Removes a specified robot from the simulation.
*   **`move_robot(name, dx, dy)`**: Commands a specific robot to move.
*   **`charge_robot(name)`**: Finds the nearest available charging station and directs the specified robot to move there and begin charging.
*   **`get_status()`**: Returns a `pandas.DataFrame` summarizing the current state of all robots.
*   **`auto_manage_batteries()`**: Starts a continuous background loop that automatically manages the charging needs of all robots.

## Usage Example

The following example demonstrates how to use the `RobotManager` to create, move, and charge a robot.

```python
import time
import threading
from RobotManager import RobotManager

# 1. Initialize the Robot Manager
manager = RobotManager()

# Start the autonomous battery management in a background thread
# This will automatically send robots to charge when their battery is low.
threading.Thread(target=manager.auto_manage_batteries, daemon=True).start()

# 2. Add a new robot to the simulation
print("--- Adding Robot 'R1' ---")
manager.add_robot("R1")
print(manager.get_status())
print("\n" + "="*30 + "\n")

# 3. Move the robot
print("--- Moving Robot 'R1' ---")
# This move is long and will consume a significant amount of battery.
manager.move_robot("R1", 50, -50)

# Wait for the move to complete (distance/velocity = duration)
# Distance = sqrt(50^2 + (-50)^2) approx 70.7
# Duration = 70.7 / 0.5 (velocity) approx 141.4 seconds
# The robot's battery will fall below 20%, triggering the auto-charge.
# We will sleep for a short time to observe its status after moving.
 time.sleep(15) 
print("\nStatus after initiating move:")
print(manager.get_status())

# The auto_manage_batteries thread will detect the low battery and
# automatically send the robot to the nearest charging station.
print("\nWaiting for auto-management to take over...")
time.sleep(30) # Allow time for the robot to move to the charging station and start charging.

print("\n--- Final Status ---")
print(manager.get_status())

# Stop the main script; daemon threads will exit.
manager.running = False
