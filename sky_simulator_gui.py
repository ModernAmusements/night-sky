import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta, timezone as dt_timezone
from skyfield.api import Star, load, Topos
from skyfield.data import hipparcos
from typing import Tuple, Optional
import warnings
import threading
import os
import time
warnings.filterwarnings('ignore')

class SkySimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sky Simulator - Interactive")
        self.root.geometry("1200x800")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Initialize sky simulator
        self.simulator = SkySimulator()
        self.current_time = datetime.now()
        self.animation_running = False
        self.animation = None
        
        # Default values
        self.latitude = 40.7128  # New York
        self.longitude = -74.0060
        self.max_magnitude = 4.5
        
        self.setup_gui()
        self.initialize_simulator()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_gui(self):
        """Setup the GUI layout"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Control Panel (Left)
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Location Settings
        location_frame = ttk.LabelFrame(control_frame, text="Location", padding="5")
        location_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(location_frame, text="Latitude:").grid(row=0, column=0, sticky=tk.W)
        self.lat_var = tk.StringVar(value=str(self.latitude))
        ttk.Entry(location_frame, textvariable=self.lat_var, width=15).grid(row=0, column=1)
        ttk.Label(location_frame, text="°N").grid(row=0, column=2)
        
        ttk.Label(location_frame, text="Longitude:").grid(row=1, column=0, sticky=tk.W)
        self.lon_var = tk.StringVar(value=str(self.longitude))
        ttk.Entry(location_frame, textvariable=self.lon_var, width=15).grid(row=1, column=1)
        ttk.Label(location_frame, text="°W").grid(row=1, column=2)
        
        # Time Settings
        time_frame = ttk.LabelFrame(control_frame, text="Time", padding="5")
        time_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(time_frame, text="Date:").grid(row=0, column=0, sticky=tk.W)
        self.date_var = tk.StringVar(value=self.current_time.strftime("%Y-%m-%d"))
        ttk.Entry(time_frame, textvariable=self.date_var, width=15).grid(row=0, column=1)
        
        ttk.Label(time_frame, text="Time:").grid(row=1, column=0, sticky=tk.W)
        self.time_var = tk.StringVar(value=self.current_time.strftime("%H:%M"))
        ttk.Entry(time_frame, textvariable=self.time_var, width=15).grid(row=1, column=1)
        
        ttk.Button(time_frame, text="Use Current Time", command=self.use_current_time).grid(row=2, column=0, columnspan=2, pady=5)
        
        # Display Settings
        display_frame = ttk.LabelFrame(control_frame, text="Display", padding="5")
        display_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(display_frame, text="Max Magnitude:").grid(row=0, column=0, sticky=tk.W)
        self.mag_var = tk.DoubleVar(value=self.max_magnitude)
        mag_scale = ttk.Scale(display_frame, from_=1, to=6, variable=self.mag_var, 
                              orient=tk.HORIZONTAL, length=150, command=self.update_magnitude)
        mag_scale.grid(row=0, column=1)
        self.mag_label = ttk.Label(display_frame, text=f"{self.max_magnitude:.1f}")
        self.mag_label.grid(row=0, column=2)
        
        # Action Buttons
        action_frame = ttk.LabelFrame(control_frame, text="Actions", padding="5")
        action_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(action_frame, text="Update Sky", command=self.update_sky).pack(fill=tk.X, pady=2)
        ttk.Button(action_frame, text="Save Image", command=self.save_image).pack(fill=tk.X, pady=2)
        
        # Animation Controls
        anim_frame = ttk.LabelFrame(control_frame, text="Animation", padding="5")
        anim_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(anim_frame, text="Duration (hours):").grid(row=0, column=0, sticky=tk.W)
        self.duration_var = tk.StringVar(value="2")
        ttk.Entry(anim_frame, textvariable=self.duration_var, width=10).grid(row=0, column=1)
        
        ttk.Label(anim_frame, text="Interval (min):").grid(row=1, column=0, sticky=tk.W)
        self.interval_var = tk.StringVar(value="10")
        ttk.Entry(anim_frame, textvariable=self.interval_var, width=10).grid(row=1, column=1)
        
        self.animate_button = ttk.Button(anim_frame, text="Start Animation", command=self.toggle_animation)
        self.animate_button.grid(row=2, column=0, columnspan=2, pady=5)
        
        # Preset Locations
        preset_frame = ttk.LabelFrame(control_frame, text="Presets", padding="5")
        preset_frame.pack(fill=tk.X)
        
        locations = [
            ("New York", 40.7128, -74.0060),
            ("London", 51.5074, -0.1278),
            ("Tokyo", 35.6762, 139.6503),
            ("Sydney", -33.8688, 151.2093)
        ]
        
        for i, (name, lat, lon) in enumerate(locations):
            ttk.Button(preset_frame, text=name, 
                      command=lambda l=lat, lo=lon: self.set_location(l, lo)).pack(fill=tk.X, pady=1)
        
        # Plot Area (Right)
        plot_frame = ttk.LabelFrame(main_frame, text="Sky View", padding="10")
        plot_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(8, 8), facecolor='black')
        self.ax = self.fig.add_subplot(111, projection='polar')
        self.setup_plot()
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def setup_plot(self):
        """Setup the polar plot"""
        self.ax.set_theta_zero_location('N')
        self.ax.set_theta_direction(-1)
        self.ax.set_ylim(0, 90)
        self.ax.set_yticks([0, 30, 60, 90])
        self.ax.set_yticklabels(['90°', '60°', '30°', '0°'])
        self.ax.grid(True, alpha=0.3)
        self.ax.set_facecolor('black')
        self.fig.patch.set_facecolor('black')
        self.ax.set_xticks(np.radians([0, 90, 180, 270]))
        self.ax.set_xticklabels(['N', 'E', 'S', 'W'], color='white')
        self.ax.tick_params(colors='white')
        
        # Add star color legend
        legend_elements = [
            ('Bright (<1 mag)', '#87CEEB'),
            ('White (1-2 mag)', 'white'), 
            ('Yellow (2-3 mag)', '#FFE4B5'),
            ('Orange (3-4 mag)', '#FFA500'),
            ('Dim (>4 mag)', '#FF6B6B')
        ]
        
        for i, (label, color) in enumerate(legend_elements):
            self.ax.scatter([], [], s=50, c=color, alpha=0.9, edgecolors='white', 
                           linewidths=0.5, label=label)
        
        self.ax.legend(loc='upper right', framealpha=0.8, labelcolor='white', 
                      fontsize=8, title='Star Magnitude', title_fontsize=9)
        
    def initialize_simulator(self):
        """Initialize the sky simulator with default settings"""
        try:
            self.status_var.set("Loading star catalog...")
            self.root.update()
            self.simulator.load_star_catalog(max_magnitude=self.max_magnitude)
            self.simulator.set_observer_location(self.latitude, self.longitude)
            self.update_sky()
            self.status_var.set("Ready")
        except Exception as e:
            messagebox.showerror("Initialization Error", f"Failed to initialize: {str(e)}")
            self.status_var.set("Error")
            
    def update_magnitude(self, value):
        """Update magnitude label and reload stars"""
        mag = float(value)
        self.mag_label.config(text=f"{mag:.1f}")
        
        if hasattr(self, 'simulator') and self.simulator.stars_df is not None:
            try:
                self.status_var.set("Reloading star catalog...")
                self.root.update()
                self.simulator.load_star_catalog(max_magnitude=mag)
                self.update_sky()
                self.status_var.set("Ready")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update magnitude: {str(e)}")
                
    def use_current_time(self):
        """Set time controls to current time"""
        now = datetime.now()
        self.date_var.set(now.strftime("%Y-%m-%d"))
        self.time_var.set(now.strftime("%H:%M"))
        self.current_time = now
        self.update_sky()
        
    def set_location(self, lat, lon):
        """Set location from preset"""
        self.lat_var.set(str(lat))
        self.lon_var.set(str(lon))
        self.latitude = lat
        self.longitude = lon
        self.update_sky()
        
    def parse_time(self):
        """Parse time from GUI inputs"""
        try:
            date_str = self.date_var.get()
            time_str = self.time_var.get()
            dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            # Ensure timezone-aware datetime
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=dt_timezone.utc)
            return dt
        except ValueError:
            raise ValueError("Invalid date/time format")
            
    def update_sky(self):
        """Update the sky view with current settings"""
        try:
            # Get parameters
            self.latitude = float(self.lat_var.get())
            self.longitude = float(self.lon_var.get())
            current_time = self.parse_time()
            
            # Update simulator
            self.simulator.set_observer_location(self.latitude, self.longitude)
            
            # Get star positions
            az, alt, sizes, colors = self.simulator.get_star_positions(current_time)
            
            # Clear and redraw
            self.ax.clear()
            self.setup_plot()
            
            if len(az) > 0:
                az_rad = np.radians(az)
                self.ax.scatter(az_rad, 90 - alt, s=sizes, c=colors, alpha=0.9, edgecolors='white', linewidths=0.5)
            else:
                self.ax.text(0, 45, "No stars visible", ha='center', va='center', 
                           color='white', fontsize=14)
            
            # Update title
            title = f'Sky View - {current_time.strftime("%Y-%m-%d %H:%M")}\n'
            title += f'Location: {self.latitude:.1f}°N, {self.longitude:.1f}°W'
            self.ax.set_title(title, color='white', fontsize=12, pad=20)
            
            self.canvas.draw()
            self.status_var.set(f"Updated - {len(az)} stars visible")
            
        except Exception as e:
            messagebox.showerror("Update Error", f"Failed to update sky: {str(e)}")
            self.status_var.set("Error")
            
    def save_image(self):
        """Save current plot to file"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
            )
            if filename:
                self.fig.savefig(filename, facecolor='black', dpi=150, bbox_inches='tight')
                messagebox.showinfo("Success", f"Image saved to {filename}")
                self.status_var.set(f"Saved to {os.path.basename(filename)}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save image: {str(e)}")
            
    def toggle_animation(self):
        """Start or stop animation"""
        if not self.animation_running:
            self.start_animation()
        else:
            self.stop_animation()
            
    def start_animation(self):
        """Start the animation"""
        try:
            duration = float(self.duration_var.get())
            interval = float(self.interval_var.get())
            start_time = self.parse_time()
            
            self.animation_running = True
            self.animate_button.config(text="Stop Animation")
            self.status_var.set("Animation running...")
            
            # Calculate number of frames
            num_frames = int(duration * 60 / interval)
            self.animation_times = [start_time + timedelta(minutes=i * interval) 
                                   for i in range(num_frames)]
            
            # Create matplotlib animation
            self.animation = FuncAnimation(
                self.fig, 
                self.update_animation_frame,
                frames=num_frames,
                interval=100,  # 100ms per frame (10 FPS for smooth animation)
                repeat=True,
                blit=False
            )
            
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Animation Error", f"Failed to start animation: {str(e)}")
            self.stop_animation()
            
    def stop_animation(self):
        """Stop the animation"""
        self.animation_running = False
        if self.animation:
            self.animation.event_source.stop()
            self.animation = None
        self.animate_button.config(text="Start Animation")
        self.status_var.set("Animation stopped")
        
    def update_animation_frame(self, frame):
        """Update a single animation frame"""
        try:
            if not self.animation_running:
                return []
                
            current_time = self.animation_times[frame]
            
            # Update time display
            self.date_var.set(current_time.strftime("%Y-%m-%d"))
            self.time_var.set(current_time.strftime("%H:%M"))
            
            # Get star positions
            az, alt, sizes, colors = self.simulator.get_star_positions(current_time)
            
            # Clear and redraw
            self.ax.clear()
            self.setup_plot()
            
            if len(az) > 0:
                az_rad = np.radians(az)
                self.ax.scatter(az_rad, 90 - alt, s=sizes, c=colors, alpha=0.9, 
                               edgecolors='white', linewidths=0.5)
            else:
                self.ax.text(0, 45, "No stars visible", ha='center', va='center', 
                           color='white', fontsize=14)
            
            # Update title
            title = f'Sky Animation - {current_time.strftime("%Y-%m-%d %H:%M")}\n'
            title += f'Location: {self.latitude:.1f}°N, {self.longitude:.1f}°W\n'
            title += f'Frame {frame + 1}/{len(self.animation_times)}'
            self.ax.set_title(title, color='white', fontsize=12, pad=20)
            
            self.canvas.draw_idle()  # More efficient than draw()
            self.status_var.set(f"Animation - Frame {frame + 1}/{len(self.animation_times)}")
            
            return []
            
        except Exception as e:
            self.status_var.set(f"Animation frame error: {str(e)}")
            return []
    
    def on_closing(self):
        """Handle window close event"""
        self.animation_running = False
        if self.animation:
            self.animation.event_source.stop()
        self.root.quit()
        self.root.destroy()


class SkySimulator:
    def __init__(self):
        self.load_planets = load('de421.bsp')
        self.earth = self.load_planets['earth']
        self.ts = load.timescale()
        self.stars_df = None
        self.observer_location = None
        self.observer_coords = None
        
    def load_star_catalog(self, max_magnitude: float = 6.0):
        """Load Hipparcos star catalog with magnitude filter"""
        with load.open(hipparcos.URL) as f:
            self.stars_df = hipparcos.load_dataframe(f)
        
        # Filter by magnitude (brightness)
        self.stars_df = self.stars_df[self.stars_df['magnitude'] <= max_magnitude]
        
    def set_observer_location(self, latitude: float, longitude: float, elevation: float = 0):
        """Set observer location on Earth"""
        self.observer_location = self.earth + Topos(latitude_degrees=latitude, 
                                                   longitude_degrees=longitude,
                                                   elevation_m=elevation)
        self.observer_coords = (latitude, longitude)
        
    def get_star_positions(self, time: datetime, timezone: str = 'UTC') -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Calculate star positions for given time with timezone handling"""
        if self.stars_df is None or self.observer_location is None:
            raise ValueError("Must load star catalog and set observer location first")
        
        # Ensure timezone-aware datetime
        if time.tzinfo is None:
            time = time.replace(tzinfo=dt_timezone.utc)
        
        # Convert to UTC for astronomical calculations
        utc_time = time.astimezone(dt_timezone.utc)
        t = self.ts.utc(utc_time.year, utc_time.month, utc_time.day, 
                       utc_time.hour, utc_time.minute, utc_time.second)
        observer = self.observer_location.at(t)
        
        star_positions = []
        star_magnitudes = []
        star_colors = []
        
        for _, star_data in self.stars_df.iterrows():
            star = Star.from_dataframe(star_data)
            astrometric = observer.observe(star)
            
            # Get altitude and azimuth
            alt, az, _ = astrometric.apparent().altaz()
            
            # Only include stars above horizon
            if alt.degrees > 0:
                star_positions.append([az.degrees, alt.degrees])
                star_magnitudes.append(star_data['magnitude'])
                
                # Color based on magnitude (brightness/temperature)
                mag = star_data['magnitude']
                if mag < 1:  # Very bright - blue/white hot stars
                    star_colors.append('#87CEEB')  # Sky blue
                elif mag < 2:  # Bright - white
                    star_colors.append('white')
                elif mag < 3:  # Medium - yellowish (like our sun)
                    star_colors.append('#FFE4B5')  # Moccasin
                elif mag < 4:  # Dim - orange
                    star_colors.append('#FFA500')  # Orange
                else:  # Very dim - red (cooler stars)
                    star_colors.append('#FF6B6B')  # Light red
        
        if not star_positions:
            return np.array([]), np.array([]), np.array([]), np.array([])
            
        positions = np.array(star_positions)
        magnitudes = np.array(star_magnitudes)
        colors = np.array(star_colors)
        
        # Convert magnitude to point size (brighter = larger)
        sizes = 20 * (5 - magnitudes) + 1
        sizes = np.clip(sizes, 1, 50)
        
        return positions[:, 0], positions[:, 1], sizes, colors


def main():
    """Run the GUI application"""
    root = tk.Tk()
    app = SkySimulatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
