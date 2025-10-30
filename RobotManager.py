from Robot import Robot
import numpy as np
import pandas as pd
import threading
import time

class RobotManager:
    def __init__(self) -> None:
        self.robots : dict[str, Robot] = {}  # Dictionary to store robots by name
        self.robots_positions = np.empty((0,2))  # Array to track all robot positions
        self.charging_stations = [np.array([0, 1]), np.array([0, 2]), np.array([0, 3])]  # Fixed charging station positions
        self.running = True   # Flag for background thread management
            
    def add_robot(self, name) -> None:
        if name in self.robots.keys():
            print(f"{name} robot exists")  # Check if robot name already exists
            return
        origin = np.array([0, 0])  # Default spawn position
        if not any(np.array_equal(origin, pos) for pos in self.robots_positions):  # Check if origin is occupied
            robot = Robot(name, position=origin)
            self.robots.update({name: robot})  # Add robot to dictionary
            self.robots_positions = np.vstack([self.robots_positions, robot.position])  # Add position to tracking array
            print(f"{robot.name} deployed at ({robot.position[0]},{robot.position[1]})")
        else:
            print("Initialization position is occupied, wait a moment and try again")
    
    def del_robot(self, name) -> None:
        if name not in self.robots:
            print("Robot with this name doesn't exist")  # Validate robot exists
            return
        robot_pos = self.robots[name].position
        global_pos = np.where(np.all(self.robots_positions == robot_pos, axis=1))[0][0]  # Find position in tracking array
        self.robots_positions = np.delete(self.robots_positions, global_pos, axis=0)  # Remove from position tracking
        del self.robots[name]  # Remove robot from dictionary
        print(f"{name} deleted")
        
    def move_robot(self, name, dx, dy) -> None:
        robot = self.robots[name]
        if robot.isCharging:
            print("Robot is currently charging, need to unplug first")  # Prevent movement while charging
            return
        old_pos = robot.position.copy()  # Store original position for updating tracking
        robot.move(dx, dy)  # Execute movement
        
        matches = np.where(np.all(self.robots_positions == old_pos, axis=1))[0]  # Find old position in tracking
        if matches.size > 0:
            self.robots_positions[matches[0]] = robot.position  # Update position in tracking array
        else:
            self.robots_positions = np.vstack([self.robots_positions, robot.position])  # Add new position if not found
        print(f"{name} has moved to ({dx}, {dy})")
        
    def charge_robot(self, name) -> None:
        if name not in self.robots:
            print("Robot with this name doesn't exist")  # Validate robot exists
            return

        robot = self.robots[name]

        if robot.isCharging:
            print("Robot is already charging")  # Check if already charging
            return

        free_stations = self.check_free_stations()  # Get available charging stations

        if free_stations.size == 0:
            print("No free Stations available")  # No stations available
            return
        
        if any(np.array_equal(robot.position, pos) for pos in free_stations):  # Check if already at free station
            robot._isCharging = True
            robot.charge()  # Start charging immediately
            print(f"{name} started charging at {robot.position}")
            return
        
        if any(np.array_equal(robot.position, pos) for pos in free_stations):  # Duplicate check (can be removed)
            robot._isCharging = True
            robot.charge()
            print(f"{name} started charging at {robot.position}")
            return

        nearest_station = self.find_nearest_station(robot.position)  # Find closest available station
        if nearest_station:
            dx = nearest_station[0] - robot.position[0]  # Calculate x movement
            dy = nearest_station[1] - robot.position[1]  # Calculate y movement

            self.move_robot(name, dx, dy)  # Move robot to station

            robot._isCharging = True
            robot.charge()  # Start charging after movement
            print(f"{name} moved to charging station and started charging")
        else:
            print("No free stations available")
            
    def stop_charging(self, name) -> None:
        robot = self.robots[name]
        robot.stop_charging()  # Delegate to robot's stop_charging method
    
    def get_status(self) -> pd.DataFrame:
        rows = []
        cols = ["Name", "Robot ID", "Battery Level", "Position", "Status"]
        for name, robot in self.robots.items():
            rows.append({"Name" : name,
                         "Robot ID" : robot.ID,
                         "Battery Level" : robot.battery_lvl,
                         "Position" : (robot.position[0], robot.position[1]),  # Convert array to tuple for DataFrame
                         "Status" : "Charging (Disabled)" if robot.isCharging else "Enabled"})  # Status based on charging state
            
        robot_dataFrame = pd.DataFrame(rows, columns= cols)  # Create pandas DataFrame
        return robot_dataFrame
            
    def check_free_stations(self) -> np.ndarray:
        free_stations = []
        for station in self.charging_stations:
            if not any(np.array_equal(station, pos) for pos in self.robots_positions):  # Check if station is occupied
                free_stations.append(station)
        return np.array(free_stations)  # Return as numpy array
    
    def find_nearest_station(self, position) -> tuple:
        free_stations = self.check_free_stations()  # Get available stations
        
        distances = np.linalg.norm(free_stations - position, axis= 1)  # Calculate distances to all free stations
        nearest_indx = np.argmin(distances)  # Find index of minimum distance
        nearest_station = free_stations[nearest_indx]
        return tuple(nearest_station)  # Return as tuple for consistency

    def auto_manage_batteries(self) -> None:
        while self.running:  # Continuous monitoring loop
            for name, robot in list(self.robots.items()):
                if robot.battery_lvl <= 20 and not robot.isCharging:  # Check if battery low and not already charging
                    threading.Thread(target=self.charge_robot, args=(name,), daemon= True).start()  # Start charging in background
        time.sleep(1)  # Check every second