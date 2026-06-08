"""
Master Controller: Koenigsegg Integrated Powertrain Simulation
Integrates Freevalve EMS + Raxial Flux Motor + LST Transmission
"""

import numpy as np
from modules.freevalve_ems import FreevalveEMS
from modules.raxial_flux_motor import RaxialFluxMotor
from modules.lst_transmission import LSTTransmission

class KoenigseggMasterController:
    def __init__(self):
        self.ems = FreevalveEMS()
        self.motor = RaxialFluxMotor()
        self.lst = LSTTransmission()
        
        # Simulation time: 0 to 30 seconds
        self.time_steps = np.linspace(0, 30, 300)
        
    def generate_drive_cycle(self):
        """
        0 to 300 km/h acceleration then cruise then deceleration
        """
        speed_profile = []
        throttle_profile = []
        rpm_profile = []

        for t in self.time_steps:
            progress = t / self.time_steps[-1]

            if progress < 0.4:
                # Hard acceleration
                speed = progress * (300 / 0.4)
                throttle = 0.85 + progress * 0.35
            elif progress < 0.7:
                # High speed cruise
                speed = 300 - np.sin(progress * 6) * 15
                throttle = 0.55 + np.sin(progress * 8) * 0.1
            else:
                # Deceleration
                speed = 300 - (progress - 0.7) * (280 / 0.3)
                throttle = 0.3 - (progress - 0.7) * 0.8

            speed = np.clip(speed, 0, 300)
            throttle = np.clip(throttle, 0.05, 1.0)
            rpm = 800 + (speed / 300) * 7200
            rpm = np.clip(rpm, 800, 8000)

            speed_profile.append(speed)
            throttle_profile.append(throttle)
            rpm_profile.append(rpm)

        return (np.array(speed_profile), 
                np.array(throttle_profile), 
                np.array(rpm_profile))

    def run(self):
        """
        Run full integrated simulation
        """
        print("=" * 55)
        print("  KOENIGSEGG INTEGRATED POWERTRAIN SIMULATION")
        print("=" * 55)
        print("  Freevalve EMS  +  Raxial Flux  +  LST")
        print("=" * 55)

        speed_profile, throttle_profile, rpm_profile = self.generate_drive_cycle()

        print("\n[1/3] Running Freevalve EMS simulation...")
        ems_results = self.ems.simulate_drive_cycle(self.time_steps)
        print("      Done.")

        print("[2/3] Running Raxial Flux Motor simulation...")
        motor_results = self.motor.simulate_drive_cycle(
            self.time_steps, rpm_profile, throttle_profile)
        print("      Done.")

        print("[3/3] Running LST Transmission simulation...")
        lst_results = self.lst.simulate_drive_cycle(
            self.time_steps, speed_profile, throttle_profile)
        print("      Done.")

        # Merge all results
        integrated = []
        for i in range(len(self.time_steps)):
            integrated.append({
                # Time & speed
                'time':                  self.time_steps[i],
                'speed':                 speed_profile[i],
                'throttle':              throttle_profile[i],
                # Freevalve
                'intake_timing':         ems_results[i]['intake_timing'],
                'exhaust_timing':        ems_results[i]['exhaust_timing'],
                'intake_lift':           ems_results[i]['intake_lift'],
                'efficiency_trad':       ems_results[i]['efficiency_traditional'],
                'efficiency_freevalve':  ems_results[i]['efficiency_freevalve'],
                # Motor
                'torque':                motor_results[i]['torque'],
                'power':                 motor_results[i]['power'],
                'motor_temp':            motor_results[i]['temperature'],
                'power_to_weight':       motor_results[i]['power_to_weight'],
                # Transmission
                'gear':                  lst_results[i]['gear'],
                'gear_rpm':              lst_results[i]['rpm'],
                'shift_occurred':        lst_results[i]['shift_occurred'],
            })

        print("\n  Simulation complete!")
        print(f"  Total time steps : {len(integrated)}")
        print(f"  Peak torque      : {max(r['torque'] for r in integrated):.1f} Nm")
        print(f"  Peak power       : {max(r['power'] for r in integrated):.1f} kW")
        print(f"  Peak speed       : {max(r['speed'] for r in integrated):.1f} km/h")
        print(f"  Total shifts     : {sum(1 for r in integrated if r['shift_occurred'])}")
        print("=" * 55)

        return integrated, self.time_steps
