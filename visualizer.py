"""
Visualizer: Koenigsegg Integrated Powertrain Simulation
Outputs: Static PNG + Animated GIF + MP4 Dashboard
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.animation import FuncAnimation, FFMpegWriter, PillowWriter
import os

# --- Color Theme (Koenigsegg-inspired) ---
BG        = '#0a0a0a'
PANEL     = '#111111'
ACCENT1   = '#ff6600'   # orange
ACCENT2   = '#00aaff'   # blue
ACCENT3   = '#00ff88'   # green
ACCENT4   = '#ffcc00'   # yellow
TEXT      = '#ffffff'
GRID      = '#222222'

def setup_style():
    plt.rcParams.update({
        'figure.facecolor':  BG,
        'axes.facecolor':    PANEL,
        'axes.edgecolor':    GRID,
        'axes.labelcolor':   TEXT,
        'xtick.color':       TEXT,
        'ytick.color':       TEXT,
        'text.color':        TEXT,
        'grid.color':        GRID,
        'grid.linestyle':    '--',
        'grid.alpha':        0.5,
        'font.family':       'monospace',
    })

def save_static_graphs(data, time_steps, output_dir='outputs'):
    setup_style()
    fig = plt.figure(figsize=(20, 14), facecolor=BG)
    fig.suptitle('KOENIGSEGG INTEGRATED POWERTRAIN SIMULATION',
                 fontsize=16, fontweight='bold', color=ACCENT1, y=0.98)

    gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.45, wspace=0.35)

    times   = [d['time']   for d in data]
    speeds  = [d['speed']  for d in data]
    torques = [d['torque'] for d in data]
    powers  = [d['power']  for d in data]
    temps   = [d['motor_temp'] for d in data]
    gears   = [d['gear']   for d in data]
    eff_t   = [d['efficiency_trad']      for d in data]
    eff_f   = [d['efficiency_freevalve'] for d in data]
    i_lift  = [d['intake_lift']  for d in data]
    i_time  = [d['intake_timing'] for d in data]
    p2w     = [d['power_to_weight'] for d in data]
    throttle= [d['throttle'] for d in data]

    # 1. Speed profile
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(times, speeds, color=ACCENT1, linewidth=2)
    ax1.fill_between(times, speeds, alpha=0.15, color=ACCENT1)
    ax1.set_title('Vehicle Speed', color=ACCENT1, fontweight='bold')
    ax1.set_ylabel('km/h'); ax1.grid(True)

    # 2. Torque & Power
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.plot(times, torques, color=ACCENT2, linewidth=2, label='Torque (Nm)')
    ax2b = ax2.twinx()
    ax2b.plot(times, powers, color=ACCENT3, linewidth=2, label='Power (kW)')
    ax2b.tick_params(colors=TEXT); ax2b.yaxis.label.set_color(TEXT)
    ax2.set_title('Torque & Power', color=ACCENT2, fontweight='bold')
    ax2.set_ylabel('Nm'); ax2b.set_ylabel('kW'); ax2.grid(True)
    ax2.legend(loc='upper left',  facecolor=PANEL, labelcolor=TEXT, fontsize=8)
    ax2b.legend(loc='upper right', facecolor=PANEL, labelcolor=TEXT, fontsize=8)

    # 3. Motor Temperature
    ax3 = fig.add_subplot(gs[0, 2])
    ax3.plot(times, temps, color=ACCENT4, linewidth=2)
    ax3.axhline(y=120, color='red', linestyle='--', alpha=0.7, label='Thermal Limit')
    ax3.fill_between(times, temps, alpha=0.15, color=ACCENT4)
    ax3.set_title('Motor Temperature', color=ACCENT4, fontweight='bold')
    ax3.set_ylabel('°C'); ax3.grid(True)
    ax3.legend(facecolor=PANEL, labelcolor=TEXT, fontsize=8)

    # 4. Gear Selection
    ax4 = fig.add_subplot(gs[1, 0])
    ax4.step(times, gears, color=ACCENT3, linewidth=2, where='post')
    ax4.fill_between(times, gears, alpha=0.15, color=ACCENT3, step='post')
    ax4.set_title('LST Gear Selection', color=ACCENT3, fontweight='bold')
    ax4.set_ylabel('Gear'); ax4.set_yticks(range(1, 8)); ax4.grid(True)

    # 5. Freevalve Efficiency
    ax5 = fig.add_subplot(gs[1, 1])
    ax5.plot(times, [e*100 for e in eff_t], color='#888888',
             linewidth=2, label='Traditional Cam', linestyle='--')
    ax5.plot(times, [e*100 for e in eff_f], color=ACCENT1,
             linewidth=2, label='Freevalve')
    ax5.fill_between(times, [e*100 for e in eff_t],
                     [e*100 for e in eff_f], alpha=0.2, color=ACCENT1)
    ax5.set_title('Freevalve vs Traditional Efficiency', color=ACCENT1, fontweight='bold')
    ax5.set_ylabel('%'); ax5.grid(True)
    ax5.legend(facecolor=PANEL, labelcolor=TEXT, fontsize=8)

    # 6. Valve Timing & Lift
    ax6 = fig.add_subplot(gs[1, 2])
    ax6.plot(times, i_time, color=ACCENT2, linewidth=2, label='Intake Timing (°)')
    ax6b = ax6.twinx()
    ax6b.plot(times, i_lift, color=ACCENT3, linewidth=1.5, label='Intake Lift (mm)')
    ax6b.tick_params(colors=TEXT); ax6b.yaxis.label.set_color(TEXT)
    ax6.set_title('Freevalve Timing & Lift', color=ACCENT2, fontweight='bold')
    ax6.set_ylabel('Degrees'); ax6b.set_ylabel('mm'); ax6.grid(True)
    ax6.legend(loc='upper left',  facecolor=PANEL, labelcolor=TEXT, fontsize=8)
    ax6b.legend(loc='upper right', facecolor=PANEL, labelcolor=TEXT, fontsize=8)

    # 7. Power-to-Weight
    ax7 = fig.add_subplot(gs[2, 0])
    ax7.plot(times, p2w, color=ACCENT4, linewidth=2)
    ax7.fill_between(times, p2w, alpha=0.15, color=ACCENT4)
    ax7.set_title('Power-to-Weight Ratio', color=ACCENT4, fontweight='bold')
    ax7.set_ylabel('kW/kg'); ax7.set_xlabel('Time (s)'); ax7.grid(True)

    # 8. Throttle Input
    ax8 = fig.add_subplot(gs[2, 1])
    ax8.plot(times, [t*100 for t in throttle], color=ACCENT2, linewidth=2)
    ax8.fill_between(times, [t*100 for t in throttle], alpha=0.15, color=ACCENT2)
    ax8.set_title('Throttle Input', color=ACCENT2, fontweight='bold')
    ax8.set_ylabel('%'); ax8.set_xlabel('Time (s)'); ax8.grid(True)

    # 9. Summary Stats
    ax9 = fig.add_subplot(gs[2, 2])
    ax9.axis('off')
    stats = [
        f"Peak Torque   : {max(torques):.0f} Nm",
        f"Peak Power    : {max(powers):.0f} kW",
        f"Peak Speed    : {max(speeds):.0f} km/h",
        f"Peak Temp     : {max(temps):.1f} °C",
        f"Total Shifts  : {sum(1 for d in data if d['shift_occurred'])}",
        f"Max Efficiency: {max(eff_f)*100:.1f}%",
        f"Max P/W Ratio : {max(p2w):.2f} kW/kg",
        f"Time Steps    : {len(data)}",
    ]
    for j, s in enumerate(stats):
        ax9.text(0.05, 0.88 - j*0.11, s,
                 transform=ax9.transAxes,
                 fontsize=10, color=ACCENT3,
                 fontfamily='monospace')
    ax9.set_title('Summary', color=ACCENT3, fontweight='bold')

    path = os.path.join(output_dir, 'static_graphs.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"  Static graphs saved -> {path}")

def save_animation(data, time_steps, output_dir='outputs'):
    setup_style()
    fig = plt.figure(figsize=(16, 9), facecolor=BG)
    fig.suptitle('KOENIGSEGG INTEGRATED POWERTRAIN SIMULATION',
                 fontsize=13, fontweight='bold', color=ACCENT1)

    gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.4, wspace=0.35)

    ax_spd  = fig.add_subplot(gs[0, 0])
    ax_trq  = fig.add_subplot(gs[0, 1])
    ax_tmp  = fig.add_subplot(gs[0, 2])
    ax_gear = fig.add_subplot(gs[1, 0])
    ax_eff  = fig.add_subplot(gs[1, 1])
    ax_info = fig.add_subplot(gs[1, 2])

    for ax, title, color in [
        (ax_spd,  'Speed (km/h)',        ACCENT1),
        (ax_trq,  'Torque (Nm)',          ACCENT2),
        (ax_tmp,  'Motor Temp (°C)',      ACCENT4),
        (ax_gear, 'Gear (LST)',           ACCENT3),
        (ax_eff,  'Efficiency (%)',       ACCENT1),
    ]:
        ax.set_title(title, color=color, fontsize=9, fontweight='bold')
        ax.set_xlim(0, time_steps[-1])
        ax.grid(True)

    times   = [d['time']   for d in data]
    speeds  = [d['speed']  for d in data]
    torques = [d['torque'] for d in data]
    temps   = [d['motor_temp'] for d in data]
    gears   = [d['gear']   for d in data]
    eff_f   = [d['efficiency_freevalve']*100 for d in data]

    ax_spd.set_ylim(0,   320)
    ax_trq.set_ylim(0,   650)
    ax_tmp.set_ylim(20,  145)
    ax_gear.set_ylim(0,  8)
    ax_eff.set_ylim(0,   55)
    ax_info.axis('off')

    ax_tmp.axhline(y=120, color='red', linestyle='--', alpha=0.6)

    line_spd,  = ax_spd.plot([], [],  color=ACCENT1, lw=2)
    line_trq,  = ax_trq.plot([], [],  color=ACCENT2, lw=2)
    line_tmp,  = ax_tmp.plot([], [],  color=ACCENT4, lw=2)
    line_gear, = ax_gear.plot([], [], color=ACCENT3, lw=2, drawstyle='steps-post')
    line_eff,  = ax_eff.plot([], [],  color=ACCENT1, lw=2)

    info_texts = []
    labels = ['Time', 'Speed', 'Torque', 'Power', 'Gear', 'Temp', 'Efficiency']
    for k, lbl in enumerate(labels):
        t = ax_info.text(0.05, 0.90 - k*0.12, '',
                         transform=ax_info.transAxes,
                         fontsize=10, color=ACCENT3, fontfamily='monospace')
        info_texts.append(t)
    ax_info.set_title('Live Data', color=ACCENT3, fontsize=9, fontweight='bold')

    STEP = 3

    def update(frame):
        i = frame * STEP
        if i >= len(data): i = len(data) - 1
        d = data[i]

        line_spd.set_data(times[:i+1],   speeds[:i+1])
        line_trq.set_data(times[:i+1],   torques[:i+1])
        line_tmp.set_data(times[:i+1],   temps[:i+1])
        line_gear.set_data(times[:i+1],  gears[:i+1])
        line_eff.set_data(times[:i+1],   eff_f[:i+1])

        info_texts[0].set_text(f"Time      : {d['time']:.1f}s")
        info_texts[1].set_text(f"Speed     : {d['speed']:.0f} km/h")
        info_texts[2].set_text(f"Torque    : {d['torque']:.0f} Nm")
        info_texts[3].set_text(f"Power     : {d['power']:.0f} kW")
        info_texts[4].set_text(f"Gear      : {d['gear']}")
        info_texts[5].set_text(f"Temp      : {d['motor_temp']:.1f} °C")
        info_texts[6].set_text(f"Efficiency: {d['efficiency_freevalve']*100:.1f}%")

        return (line_spd, line_trq, line_tmp, line_gear,
                line_eff, *info_texts)

    total_frames = len(data) // STEP
    anim = FuncAnimation(fig, update, frames=total_frames,
                         interval=50, blit=True)

    # Save GIF
    gif_path = os.path.join(output_dir, 'dashboard.gif')
    print("  Saving GIF (this may take ~30 seconds)...")
    anim.save(gif_path, writer=PillowWriter(fps=20))
    print(f"  GIF saved -> {gif_path}")

    # Save MP4
    mp4_path = os.path.join(output_dir, 'dashboard.mp4')
    print("  Saving MP4...")
    try:
        writer = FFMpegWriter(fps=30, bitrate=1800)
        anim.save(mp4_path, writer=writer)
        print(f"  MP4 saved -> {mp4_path}")
    except Exception as e:
        print(f"  MP4 skipped (ffmpeg not found): {e}")

    plt.close()
