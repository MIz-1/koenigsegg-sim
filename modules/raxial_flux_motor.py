"""
Module 2: Raxial Flux Motor (Koenigsegg Quark-inspired)
Powertrain Digital Twin — Torque + Thermal Simulation
"""

import numpy as np

class RaxialFluxMotor:
    def __init__(self):
        # Quark motor specs
        self.peak_torque = 600        # Nm
        self.peak_power = 335         # kW
        self.mass = 28.5              # kg
        self.max_rpm = 8500
        self.thermal_limit = 120      # Celsius
        self.ambient_temp = 25        # Celsius
        
    def torque_model(self, rpm, throttle):
        """
        Raxial Flux torque delivery curve
        Combines axial (high torque) + radial (high RPM) characteristics
        """
        throttle = np.clip(throttle, 0.0, 1.0)
        rpm = np.clip(rpm, 0, self.max_rpm)
        
        # Axial flux component — high torque at low RPM
        axial_torque = self.peak_torque * 0.6 * np.exp(-rpm / 3000)
        
        # Radial flux component — sustains power at high RPM
        radial_torque = self.peak_torque * 0.4 * (1 - (rpm / self.max_rpm) ** 2)
        
        # Combined Raxial torque
        raw_torque = (axial_torque + radial_torque) * throttle
        
        return np.clip(raw_torque, 0, self.peak_torque)
    
    def power_output(self, rpm, throttle):
        """Power in kW"""
        torque = self.torque_model(rpm, throttle)
        power = (torque * rpm * 2 * np.pi) / (60 * 1000)
        return np.clip(power, 0, self.peak_power)
    
    def thermal_model(self, rpm, throttle, duration, prev_temp):
        """
        Motor temperature rise simulation
        """
        power = self.power_output(rpm, throttle)
        
        # Heat generation (watts lost as heat ~8% of power)
        heat_generated = power * 1000 * 0.08
        
        # Cooling (natural + forced air)
        cooling_rate = 15 + (rpm / self.max_rpm) * 35
        heat_dissipated = cooling_rate * (prev_temp - self.ambient_temp)
        
        # Temperature delta
        thermal_mass = self.mass * 500  # specific heat capacity approx
        delta_temp = ((heat_generated - heat_dissipated) / thermal_mass) * duration
        
        new_temp = prev_temp + delta_temp
        return np.clip(new_temp, self.ambient_temp, self.thermal_limit + 20)
    
    def torque_vectoring(self, rpm_fl, rpm_fr, rpm_rl, rpm_rr, throttle, steering_angle):
        """
        Dual Quark motor torque vectoring across 4 corners
        """
        base_torque = self.torque_model(np.mean([rpm_fl, rpm_fr, rpm_rl, rpm_rr]), throttle)
        
        # Steering correction
        steering_factor = steering_angle / 45.0  # normalize to -1 to 1
        
        torques = {
            'front_left':  base_torque * (1 - steering_factor * 0.2),
            'front_right': base_torque * (1 + steering_factor * 0.2),
            'rear_left':   base_torque * (1 - steering_factor * 0.15),
            'rear_right':  base_torque * (1 + steering_factor * 0.15)
        }
        return torques
    
    def simulate_drive_cycle(self, time_steps, rpm_profile, throttle_profile):
        """
        Full drive cycle simulation with thermal tracking
        """
        results = []
        temp = self.ambient_temp
        
        for i, t in enumerate(time_steps):
            rpm = rpm_profile[i]
            throttle = throttle_profile[i]
            dt = time_steps[1] - time_steps[0]
            
            torque = self.torque_model(rpm, throttle)
            power = self.power_output(rpm, throttle)
            temp = self.thermal_model(rpm, throttle, dt, temp)
            
            # Power to weight ratio (kW/kg)
            power_to_weight = power / self.mass
            
            results.append({
                'time': t,
                'rpm': rpm,
                'throttle': throttle,
                'torque': torque,
                'power': power,
                'temperature': temp,
                'power_to_weight': power_to_weight,
                'thermal_warning': temp > self.thermal_limit
            })
        
        return results
