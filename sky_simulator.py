import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.projections import PolarAxes
from datetime import datetime, timedelta, timezone as dt_timezone
from skyfield.api import Star, load, Topos
from skyfield.data import hipparcos
from typing import Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

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
        print(f"Loaded {len(self.stars_df)} stars with magnitude <= {max_magnitude}")
        
    def set_observer_location(self, latitude: float, longitude: float, elevation: float = 0):
        """Set observer location on Earth"""
        self.observer_location = self.earth + Topos(latitude_degrees=latitude, 
                                                   longitude_degrees=longitude,
                                                   elevation_m=elevation)
        self.observer_coords = (latitude, longitude)
        
    def get_star_positions(self, time: datetime, timezone: str = 'UTC') -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Calculate star positions for given time with timezone handling"""
        if self.stars_df is None or self.observer_location is None:
            raise ValueError("Must load star catalog and set observer location first")
        
        # Handle timezone - assume naive datetime is UTC for simplicity
        if time.tzinfo is None:
            time = time.replace(tzinfo=dt_timezone.utc)
        
        # Convert to UTC for astronomical calculations
        utc_time = time.astimezone(dt_timezone.utc)
        t = self.ts.utc(utc_time.year, utc_time.month, utc_time.day, 
                       utc_time.hour, utc_time.minute, utc_time.second)
        observer = self.observer_location.at(t)
        
        star_positions = []
        star_magnitudes = []
        
        for _, star_data in self.stars_df.iterrows():
            star = Star.from_dataframe(star_data)
            astrometric = observer.observe(star)
            
            # Get altitude and azimuth
            alt, az, _ = astrometric.apparent().altaz()
            
            # Only include stars above horizon
            if alt.degrees > 0:
                star_positions.append([az.degrees, alt.degrees])
                star_magnitudes.append(star_data['magnitude'])
        if not star_positions:
            return np.array([]), np.array([]), np.array([])
            
        positions = np.array(star_positions)
        magnitudes = np.array(star_magnitudes)
        
        # Convert magnitude to point size (brighter = larger)
        sizes = 20 * (5 - magnitudes) + 1
        sizes = np.clip(sizes, 1, 50)
        
        return positions[:, 0], positions[:, 1], sizes
        
    def plot_sky(self, time: datetime, save_path: Optional[str] = None, timezone: str = 'UTC'):
        """Create a polar plot of the sky at given time"""
        az, alt, sizes = self.get_star_positions(time, timezone)
        
        # Handle case when no stars are visible
        if len(az) == 0:
            print("No stars visible at this time/location")
            return
        
        # Create figure with polar projection
        fig, ax = plt.subplots(figsize=(12, 12), subplot_kw=dict(projection='polar'))  # type: ignore
        
        # Convert to radians for polar plot
        az_rad = np.radians(az)
        
        # Plot stars
        ax.scatter(az_rad, 90 - alt, s=sizes, c='white', alpha=0.8)
        
        # Customize plot - using type comment for polar axes methods
        ax.set_theta_zero_location('N')  # type: ignore
        ax.set_theta_direction(-1)        # type: ignore       # Clockwise
        # Set radius from center (90° at center, 0° at edge)
        ax.set_ylim(0, 90)
        ax.set_yticks([0, 30, 60, 90])
        ax.set_yticklabels(['90°', '60°', '30°', '0°'])
        
        # Configure grid and labels
        ax.grid(True, alpha=0.3)
        ax.set_facecolor('black')
        fig.patch.set_facecolor('black')
        
        # Add compass directions
        ax.set_xticks(np.radians([0, 90, 180, 270]))
        ax.set_xticklabels(['N', 'E', 'S', 'W'], color='white')
        ax.tick_params(colors='white')
        
        # Add title with time and location info
        if self.observer_coords is not None:
            lat, lon = self.observer_coords
            title = f'Sky View - {time.strftime("%Y-%m-%d %H:%M")}\n'
            title += f'Location: {lat:.1f}°N, {lon:.1f}°W'
        else:
            title = f'Sky View - {time.strftime("%Y-%m-%d %H:%M")}\nLocation: Unknown'
        
        ax.set_title(title, color='white', fontsize=14, pad=20)
        # Create legend with magnitude examples
        mag_examples = [1, 3, 5]  # Example magnitudes
        for mag in mag_examples:
            size = 20 * (5 - mag) + 1
            size = np.clip(size, 1, 50)
            ax.scatter([], [], s=size, c='white', alpha=0.8, 
                      label=f'Mag {mag}')
        ax.legend(loc='upper right', framealpha=0.8, labelcolor='white')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, facecolor='black', dpi=150, bbox_inches='tight')
        else:
            plt.show()
            
    def create_star_trails(self, start_time: datetime, duration_hours: float, 
                           interval_minutes: float = 15, save_path: Optional[str] = None, timezone: str = 'UTC'):
        """Create an image showing star trails over time"""
        num_frames = int(duration_hours * 60 / interval_minutes)
        times = [start_time + timedelta(minutes=i * interval_minutes) 
                for i in range(num_frames)]
        
        # Create figure with polar projection
        fig, ax = plt.subplots(figsize=(12, 12), subplot_kw=dict(projection='polar'))  # type: ignore
        ax.set_theta_zero_location('N')  # North at top  # type: ignore
        ax.set_theta_direction(-1)       # Clockwise  # type: ignore
        ax.set_ylim(0, 90)
        ax.set_facecolor('black')
        fig.patch.set_facecolor('black')
        
        # Plot star trails
        for i, time in enumerate(times):
            az, alt, sizes = self.get_star_positions(time, timezone)
            if len(az) > 0:
                az_rad = np.radians(az)
                alpha = 0.1 + 0.9 * (i / num_frames)  # Fade in effect
                ax.scatter(az_rad, 90 - alt, s=sizes, c='white', alpha=alpha)
            elif i == 0:  # Only warn once if first frame has no stars
                print("Warning: No stars visible at start time")
        
        # Configure plot
        ax.grid(True, alpha=0.3)
        ax.set_xticks(np.radians([0, 90, 180, 270]))
        ax.set_xticklabels(['N', 'E', 'S', 'W'], color='white')
        ax.tick_params(colors='white')
        
        # Add title
        if self.observer_coords is not None:
            lat, lon = self.observer_coords
            title = f'Star Trails - {duration_hours:.1f} hours\n'
            title += f'Start: {start_time.strftime("%Y-%m-%d %H:%M")}\n'
            title += f'Location: {lat:.1f}°N, {lon:.1f}°W'
        else:
            title = f'Star Trails - {duration_hours:.1f} hours\nStart: {start_time.strftime("%Y-%m-%d %H:%M")}\nLocation: Unknown'
        ax.set_title(title, color='white', fontsize=14, pad=20)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, facecolor='black', dpi=150, bbox_inches='tight')
        else:
            plt.show()
            
    def animate_sky(self, start_time: datetime, duration_hours: float, 
                   interval_minutes: float = 10, save_path: Optional[str] = None, timezone: str = 'UTC'):
        """Create animated visualization of sky over time"""
        num_frames = int(duration_hours * 60 / interval_minutes)
        
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))  # type: ignore
        ax.set_theta_zero_location('N')  # type: ignore
        ax.set_theta_direction(-1)  # type: ignore
        ax.set_ylim(0, 90)
        ax.set_facecolor('black')
        fig.patch.set_facecolor('black')
        
        def animate(frame):
            ax.clear()
            
            current_time = start_time + timedelta(minutes=frame * interval_minutes)
            az, alt, sizes = self.get_star_positions(current_time, timezone)
            
            if len(az) > 0:
                az_rad = np.radians(az)
                ax.scatter(az_rad, 90 - alt, s=sizes, c='white', alpha=0.8)
            
            ax.set_theta_zero_location('N')   # North at top  # type: ignore
            ax.set_theta_direction(-1)        # Clockwise  # type: ignore
            ax.set_ylim(0, 90)
            ax.set_yticks([0, 30, 60, 90])
            ax.set_yticklabels(['90°', '60°', '30°', '0°'])
            ax.grid(True, alpha=0.3)
            ax.set_facecolor('black')
            ax.set_xticks(np.radians([0, 90, 180, 270]))
            ax.set_xticklabels(['N', 'E', 'S', 'W'], color='white')
            ax.tick_params(colors='white')
            
            # Update title
            if self.observer_coords is not None:
                lat, lon = self.observer_coords
                title = f'Sky Animation - {current_time.strftime("%Y-%m-%d %H:%M")}\n'
                title += f'Location: {lat:.1f}°N, {lon:.1f}°W'
            else:
                title = f'Sky Animation - {current_time.strftime("%Y-%m-%d %H:%M")}\nLocation: Unknown'
            ax.set_title(title, color='white', fontsize=12, pad=20)
            
            return []
        
        anim = FuncAnimation(fig, animate, frames=num_frames, interval=200, blit=False)
        
        if save_path:
            anim.save(save_path, writer='pillow', fps=5)
        else:
            plt.show()

def main():
    """Example usage of the SkySimulator"""
    # Initialize simulator
    simulator = SkySimulator()
    
    # Load star catalog (stars up to magnitude 4.5 for faster processing)
    print("Loading star catalog...")
    simulator.load_star_catalog(max_magnitude=4.5)
    
    # Set observer location (New York City)
    simulator.set_observer_location(latitude=40.7128, longitude=-74.0060)
    
    # Set time for observation
    observation_time = datetime(2024, 6, 15, 22, 0, 0)  # June 15, 2024 at 10 PM
    
    print(f"Generating sky view for {observation_time}")
    
    # Create static sky view
    simulator.plot_sky(observation_time, save_path='sky_view.png')
    
    # Create star trails (6 hours)
    print("Generating star trails...")
    simulator.create_star_trails(observation_time, duration_hours=6, 
                                save_path='star_trails.png')
    
    # Create animation (2 hours)
    print("Creating animation...")
    simulator.animate_sky(observation_time, duration_hours=2, 
                         interval_minutes=15, save_path='sky_animation.gif')
    
    print("Simulation complete! Check the generated files.")

if __name__ == "__main__":
    main()