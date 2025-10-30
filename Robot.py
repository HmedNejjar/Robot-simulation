import numpy as np
import time
import random as rand
import threading

class Robot:
    def __init__(self, name, position = None) -> None:
        self.name = name
        self._ID = rand.randint(1000, 100000000)  # Generate unique ID for each robot
        self.position = np.array([0,0]) if position is None else position  # Default to origin if no position provided
        self._battery_lvl = 100.00 # Private variable - current battery percentage
        self._isCharging = False # Private variable - charging state flag
        self._charging_rate = 0.2 # Private variable - battery percentage increase per second
        self._velocity = 0.5  # Movement speed units per second
    
    def __repr__(self) -> str:
        return self.get_status()  # String representation shows robot status
    
    @property
    def battery_lvl(self) -> float:
        return float(self._battery_lvl)  # Property getter for battery level
    @property
    def isCharging(self) -> bool:
        return self._isCharging  # Property getter for charging status
    @property
    def charging_rate(self) -> float:
        return self._charging_rate   # Property getter for charging rate
    @property
    def velocity(self) -> float:
        return self._velocity  # Property getter for movement velocity
    @property
    def ID(self) -> int:
        return self._ID  # Property getter for robot ID
    
    def get_status(self):
        charging = "Charging" if self.isCharging else "Running"  # Determine status string
        return f"Robot Name: {self.name}\nRobot ID: {self.ID}\nBattery Level: {self.battery_lvl}\nCurrent Position: {self.position}\nStatus: {charging}" 

    def charge(self) -> None:
        if self._battery_lvl >= 100:
            print(f"{self.name} is already fully charged! ⚡")
            return
        
        def charging_loop():
            self._isCharging = True  # Set charging flag
            last_update = time.time()  # Track time for delta calculation
            
            while self.isCharging and self.battery_lvl < 100:  # Continue until full or stopped
                current_time = time.time()
                delta_time = current_time - last_update  # Calculate time since last update
                self._battery_lvl = min(100, self.battery_lvl + delta_time * self.charging_rate)  # Increase battery, cap at 100
                time.sleep(0.1)  # Small delay to prevent excessive CPU usage

        threading.Thread(target=charging_loop, daemon=True).start()  # Run charging in background thread
        
    def stop_charging(self) -> None:
        self._isCharging = False  # Stop charging by setting flag
        
    def move(self, dx, dy) -> None:
        if self.isCharging or self.battery_lvl == 0:  # Prevent movement while charging or no battery
            return
        delta = np.array([dx, dy])  # Create movement vector
        distance = np.linalg.norm(delta)  # Calculate Euclidean distance
        duration = float(distance) / float(self._velocity)  # Calculate time needed for movement
        time.sleep(duration)  # Simulate movement time
        self.position += delta  # Update position
        consumption_lvl = distance * 0.1  # Calculate battery consumption
        self._battery_lvl = max(0.0, self._battery_lvl - consumption_lvl)  # Decrease battery, minimum 0