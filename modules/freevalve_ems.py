"""
Module 1: Freevalve Engine Management System (EMS)
Koenigsegg-inspired camless valve timing simulation
"""

import numpy as np

class FreevalveEMS:
    def __init__(self):
        self.rpm_range = np.linspace(800, 8000, 500)
        
    def valve_timing(self, rpm, throttle, load):
        """
        Dynamic valve timing based on operating conditions
        throttle: 0.0 to 1.0
        load: 0.0 to 1.0
        """
        # Base timing advance (degrees)
        base_advance = 10 + (rpm / 8000) * 30
        
        # Throttle correction
        throttle_correction = throttle * 15
        
        # Load correction
        load_correction = load * 10
        
        # Freevalve can optimize independently
        intake_timing = base_advance + throttle_correction
        exhaust_timing = base_advance + load_correction
        
        # Valve lift (mm) — freevalve adjusts this too
        intake_lift = 4 + throttle * 8     # 4mm to 12mm
        exhaust_lift = 4 + load * 6        # 4mm to 10mm
        
        return {
            'intake_timing': intake_timing,
            'exhaust_timing': exhaust_timing,
            'intake_lift': intake_lift,
            'exhaust_lift': exhaust_lift
        }
    
    def efficiency(self, rpm, throttle, load):
        """
        Thermal efficiency comparison: Freevalve vs Traditional Cam
        """
        timing = self.valve_timing(rpm, throttle, load)
        
        # Traditional cam — fixed timing, efficiency drops at extremes
        trad_efficiency = 0.38 * np.exp(-((rpm - 4000) ** 2) / (2 * 1500 ** 2))
        trad_efficiency = np.clip(trad_efficiency, 0.15, 0.38)
        
        # Freevalve — optimized at every RPM point
        freevalve_efficiency = 0.45 * (1 - 0.3 * np.exp(-rpm / 3000))
        freevalve_efficiency *= (0.7 + 0.3 * throttle)
        freevalve_efficiency = np.clip(freevalve_efficiency, 0.18, 0.45)
        
        return {
            'traditional': float(trad_efficiency),
            'freevalve': float(freevalve_efficiency),
            'gain': float(freevalve_efficiency - trad_efficiency)
        }
    
    def simulate_drive_cycle(self, time_steps):
        """
        Simulate valve behavior over a full drive cycle
        """
        results = []
        for t in time_steps:
            # Drive cycle: acceleration then cruise then deceleration
            progress = t / time_steps[-1]
            
            if progress < 0.4:
                rpm = 800 + progress * (7000 / 0.4)
                throttle = 0.3 + progress * 1.5
                load = 0.4 + progress * 1.2
            elif progress < 0.7:
                rpm = 4500 + np.sin(progress * 10) * 300
                throttle = 0.6 + np.sin(progress * 8) * 0.1
                load = 0.5
            else:
                rpm = 7000 - (progress - 0.7) * (6000 / 0.3)
                throttle = 0.9 - (progress - 0.7) * 2.5
                load = 0.7 - (progress - 0.7) * 1.5
            
            rpm = np.clip(rpm, 800, 8000)
            throttle = np.clip(throttle, 0.1, 1.0)
            load = np.clip(load, 0.1, 1.0)
            
            timing = self.valve_timing(rpm, throttle, load)
            eff = self.efficiency(rpm, throttle, load)
            
            results.append({
                'time': t,
                'rpm': rpm,
                'throttle': throttle,
                'load': load,
                'intake_timing': timing['intake_timing'],
                'exhaust_timing': timing['exhaust_timing'],
                'intake_lift': timing['intake_lift'],
                'exhaust_lift': timing['exhaust_lift'],
                'efficiency_traditional': eff['traditional'],
                'efficiency_freevalve': eff['freevalve']
            })
        
        return results
