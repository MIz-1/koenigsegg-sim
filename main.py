"""
Main Entry Point: Koenigsegg Integrated Powertrain Simulation
© 2026 MIz-1 — All Rights Reserved
"""

from master_controller import KoenigseggMasterController
from visualizer import save_static_graphs, save_animation
import os

def main():
    print("\n")
    print("  ██╗  ██╗ ██████╗ ███████╗███╗   ██╗██╗ ██████╗ ")
    print("  ██║ ██╔╝██╔═══██╗██╔════╝████╗  ██║██║██╔════╝ ")
    print("  █████╔╝ ██║   ██║█████╗  ██╔██╗ ██║██║██║  ███╗")
    print("  ██╔═██╗ ██║   ██║██╔══╝  ██║╚██╗██║██║██║   ██║")
    print("  ██║  ██╗╚██████╔╝███████╗██║ ╚████║██║╚██████╔╝")
    print("  ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝╚═╝ ╚═════╝ ")
    print("")
    print("  Integrated Powertrain Simulation v1.0")
    print("  Freevalve EMS + Raxial Flux Motor + LST")
    print("  © 2026 MIz-1 — All Rights Reserved")
    print("\n")

    # Ensure output directory exists
    os.makedirs('outputs', exist_ok=True)

    # Run master simulation
    controller = KoenigseggMasterController()
    data, time_steps = controller.run()

    # Generate outputs
    print("\n[Visualizer] Generating outputs...")
    print("")

    print("  [1/3] Static graphs...")
    save_static_graphs(data, time_steps)

    print("  [2/3] Animated dashboard...")
    save_animation(data, time_steps)

    print("\n")
    print("=" * 55)
    print("  ALL OUTPUTS SAVED TO: outputs/")
    print("  - static_graphs.png")
    print("  - dashboard.gif")
    print("  - dashboard.mp4")
    print("=" * 55)
    print("")

if __name__ == "__main__":
    main()
