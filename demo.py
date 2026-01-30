#!/usr/bin/env python3
"""
Interactive Sky Simulator Demo
Demonstrates the sky simulation from multiple locations and times
"""

from sky_simulator import SkySimulator
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np

def demo_multiple_locations():
    """Show sky views from different locations at the same time"""
    simulator = SkySimulator()
    simulator.load_star_catalog(max_magnitude=4.0)
    
    # Define locations (latitude, longitude, name)
    locations = [
        (40.7128, -74.0060, "New York"),
        (51.5074, -0.1278, "London"),
        (-33.8688, 151.2093, "Sydney"),
        (35.6762, 139.6503, "Tokyo"),
        (64.2008, -149.4937, "Fairbanks (Alaska)")
    ]
    
    # Set observation time
    observation_time = datetime(2024, 6, 15, 22, 0, 0)
    
    # Create subplots for each location
    fig, axes = plt.subplots(2, 3, figsize=(18, 12), subplot_kw=dict(projection='polar'))
    axes = axes.flatten()
    
    for i, (lat, lon, name) in enumerate(locations):
        if i >= len(axes):
            break
            
        simulator.set_observer_location(lat, lon)
        az, alt, sizes = simulator.get_star_positions(observation_time)
        
        ax = axes[i]
        
        if len(az) > 0:
            az_rad = np.radians(az)
            ax.scatter(az_rad, 90 - alt, s=sizes, c='white', alpha=0.8)
        
        # Configure subplot
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        ax.set_ylim(0, 90)
        ax.set_facecolor('black')
        ax.grid(True, alpha=0.3)
        ax.set_xticks(np.radians([0, 90, 180, 270]))
        ax.set_xticklabels(['N', 'E', 'S', 'W'], color='white', fontsize=8)
        ax.tick_params(colors='white', labelsize=8)
        ax.set_title(f'{name}\n{lat:.1f}°N, {lon:.1f}°W', color='white', fontsize=10)
    
    # Hide unused subplot
    if len(locations) < len(axes):
        axes[-1].set_visible(False)
    
    fig.suptitle(f'Sky Views - {observation_time.strftime("%Y-%m-%d %H:%M UTC")}', 
                 color='white', fontsize=16)
    fig.patch.set_facecolor('black')
    plt.tight_layout()
    plt.savefig('multiple_locations.png', facecolor='black', dpi=150, bbox_inches='tight')
    plt.show()

def demo_time_lapse():
    """Show how the sky changes over time from one location"""
    simulator = SkySimulator()
    simulator.load_star_catalog(max_magnitude=3.5)  # Fewer stars for clarity
    
    # Set location (New York)
    simulator.set_observer_location(40.7128, -74.0060)
    
    # Create time series (every 2 hours over 24 hours)
    start_time = datetime(2024, 6, 15, 18, 0, 0)  # 6 PM
    times = [start_time + timedelta(hours=i) for i in range(0, 25, 2)]
    
    # Create subplots
    fig, axes = plt.subplots(3, 4, figsize=(16, 12), subplot_kw=dict(projection='polar'))
    axes = axes.flatten()
    
    for i, time in enumerate(times):
        if i >= len(axes):
            break
            
        az, alt, sizes = simulator.get_star_positions(time)
        ax = axes[i]
        
        if len(az) > 0:
            az_rad = np.radians(az)
            ax.scatter(az_rad, 90 - alt, s=sizes, c='white', alpha=0.8)
        
        # Configure subplot
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        ax.set_ylim(0, 90)
        ax.set_facecolor('black')
        ax.grid(True, alpha=0.3)
        ax.set_xticks(np.radians([0, 90, 180, 270]))
        ax.set_xticklabels(['N', 'E', 'S', 'W'], color='white', fontsize=8)
        ax.tick_params(colors='white', labelsize=8)
        ax.set_title(f'{time.strftime("%H:%M")}', color='white', fontsize=10)
    
    fig.suptitle('New York Sky - 24 Hour Time Lapse (June 15, 2024)', 
                 color='white', fontsize=16)
    fig.patch.set_facecolor('black')
    plt.tight_layout()
    plt.savefig('time_lapse.png', facecolor='black', dpi=150, bbox_inches='tight')
    plt.show()

def demo_seasonal_comparison():
    """Compare the sky at the same time in different seasons"""
    simulator = SkySimulator()
    simulator.load_star_catalog(max_magnitude=4.0)
    
    # Set location (mid-latitude)
    simulator.set_observer_location(45.0, -122.0)  # Oregon
    
    # Define seasons (same time, different months)
    seasons = [
        (datetime(2024, 3, 21, 21, 0, 0), "Spring Equinox"),
        (datetime(2024, 6, 21, 21, 0, 0), "Summer Solstice"),
        (datetime(2024, 9, 21, 21, 0, 0), "Fall Equinox"),
        (datetime(2024, 12, 21, 21, 0, 0), "Winter Solstice")
    ]
    
    # Create subplots
    fig, axes = plt.subplots(2, 2, figsize=(12, 12), subplot_kw=dict(projection='polar'))
    axes = axes.flatten()
    
    for i, (time, season_name) in enumerate(seasons):
        az, alt, sizes = simulator.get_star_positions(time)
        ax = axes[i]
        
        if len(az) > 0:
            az_rad = np.radians(az)
            ax.scatter(az_rad, 90 - alt, s=sizes, c='white', alpha=0.8)
        
        # Configure subplot
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        ax.set_ylim(0, 90)
        ax.set_facecolor('black')
        ax.grid(True, alpha=0.3)
        ax.set_xticks(np.radians([0, 90, 180, 270]))
        ax.set_xticklabels(['N', 'E', 'S', 'W'], color='white')
        ax.tick_params(colors='white')
        ax.set_title(f'{season_name}\n{time.strftime("%B %d, 21:00")}', 
                    color='white', fontsize=12)
    
    fig.suptitle('Seasonal Sky Comparison - Oregon (45°N, 122°W)', 
                 color='white', fontsize=16)
    fig.patch.set_facecolor('black')
    plt.tight_layout()
    plt.savefig('seasonal_comparison.png', facecolor='black', dpi=150, bbox_inches='tight')
    plt.show()

def main():
    """Run all demos"""
    print("Generating Multiple Locations Demo...")
    demo_multiple_locations()
    
    print("Generating Time Lapse Demo...")
    demo_time_lapse()
    
    print("Generating Seasonal Comparison Demo...")
    demo_seasonal_comparison()
    
    print("All demos complete! Check the generated PNG files.")

if __name__ == "__main__":
    main()