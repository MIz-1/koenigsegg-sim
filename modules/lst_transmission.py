"""
Module 3: Light Speed Transmission (LST)
Koenigsegg-inspired Predictive Shifting Algorithm
Non-sequential gear shifting simulation
"""

import numpy as np

class LSTTransmission:
    def __init__(self):
        # 7-speed LST gear ratios
        self.gear_ratios = {
            1: 4.50,
            2: 3.20,
            3: 2.40,
            4: 1.80,
            5: 1.35,
            6: 1.00,
            7: 0.75
        }
        self.final_drive = 3.27
        self.current_gear = 1
        self.shift_time = 0.002   # 2ms — Light Speed Shifting
        self.trad_shift_time = 0.200  # 200ms — traditional sequential
        
        # 9 clutch engagement map (which clutches for which gear)
        self.clutch_map = {
            1: [1, 2],
            2: [1, 3],
            3: [2, 4],
            4: [2, 5],
            5: [3, 6],
            6: [3, 7],
            7: [4, 8]
        }
    
    def wheel_speed_to_rpm(self, speed_kmh, gear):
        """Convert vehicle speed to engine RPM for given gear"""
        speed_ms = speed_kmh / 3.6
        wheel_radius = 0.35  # meters
        wheel_rpm = (speed_ms / (2 * np.pi * wheel_radius)) * 60
        engine_rpm = wheel_rpm * self.gear_ratios[gear] * self.final_drive
        return np.clip(engine_rpm, 800, 8500)
    
    def predict_optimal_gear(self, speed_kmh, throttle, acceleration):
        """
        AI Predictive Shifting — finds optimal gear
        based on speed, throttle demand, and acceleration intent
        """
        best_gear = 1
        best_score = -np.inf
        
        for gear in range(1, 8):
            rpm = self.wheel_speed_to_rpm(speed_kmh, gear)
            
            # RPM efficiency window (2500-6000 is sweet spot)
            rpm_score = -abs(rpm - 4000) / 4000
            
            # Throttle demand — high throttle wants lower gear
            throttle_score = -throttle * (gear / 7)
            
            # Acceleration intent
            accel_score = acceleration * (1 / gear)
            
            # Avoid redline or stall
            validity = 1.0 if 800 < rpm < 8000 else -10.0
            
            total_score = (rpm_score * 0.5 + 
                          throttle_score * 0.3 + 
                          accel_score * 0.2 + validity)
            
            if total_score > best_score:
                best_score = total_score
                best_gear = gear
        
        return best_gear
    
    def light_speed_shift(self, from_gear, to_gear):
        """
        Non-sequential shifting — LST can jump any gear directly
        e.g., 7th -> 3rd instantly (impossible in traditional gearbox)
        """
        gear_jump = abs(to_gear - from_gear)
        
        # Traditional sequential must go through each gear
        trad_time = gear_jump * self.trad_shift_time
        
        # LST — direct engagement regardless of jump size
        lst_time = self.shift_time
        
        # Clutch engagement sequence
        outgoing_clutches = self.clutch_map[from_gear]
        incoming_clutches = self.clutch_map[to_gear]
        
        return {
            'from_gear': from_gear,
            'to_gear': to_gear,
            'gear_jump': gear_jump,
            'lst_shift_time': lst_time,
            'traditional_shift_time': trad_time,
            'time_saved': trad_time - lst_time,
            'outgoing_clutches': outgoing_clutches,
            'incoming_clutches': incoming_clutches,
            'non_sequential': gear_jump > 1
        }
    
    def simulate_drive_cycle(self, time_steps, speed_profile, throttle_profile):
        """
        Full transmission simulation over drive cycle
        """
        results = []
        current_gear = 1
        prev_speed = 0
        
        for i, t in enumerate(time_steps):
            speed = speed_profile[i]
            throttle = throttle_profile[i]
            dt = time_steps[1] - time_steps[0]
            
            # Acceleration
            acceleration = (speed - prev_speed) / dt if dt > 0 else 0
            prev_speed = speed
            
            # Predict optimal gear
            optimal_gear = self.predict_optimal_gear(speed, throttle, acceleration)
            
            # Shift if needed
            shift_occurred = optimal_gear != current_gear
            shift_data = None
            
            if shift_occurred:
                shift_data = self.light_speed_shift(current_gear, optimal_gear)
                current_gear = optimal_gear
            
            rpm = self.wheel_speed_to_rpm(speed, current_gear)
            
            results.append({
                'time': t,
                'speed': speed,
                'throttle': throttle,
                'gear': current_gear,
                'rpm': rpm,
                'acceleration': acceleration,
                'shift_occurred': shift_occurred,
                'shift_data': shift_data,
                'gear_ratio': self.gear_ratios[current_gear]
            })
        
        return results
