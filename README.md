# Sky and Stars Simulation

A Python-based astronomical simulator that visualizes the night sky and star paths from any point on Earth.

## Features

- **Real-time star positions** using the Hipparcos star catalog
- **Location-based viewing** from any latitude/longitude on Earth
- **Multiple visualization modes**:
  - Static sky views at specific times
  - Star trails showing celestial motion over time
  - Animated sky simulations
  - Multi-location comparisons
- **Time controls** for different dates, seasons, and times of day
- **Accurate celestial mechanics** using the Skyfield library

## Installation

1. Clone or download this repository
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

```python
from sky_simulator import SkySimulator
from datetime import datetime

# Initialize simulator
simulator = SkySimulator()
simulator.load_star_catalog(max_magnitude=4.5)

# Set your location (latitude, longitude)
simulator.set_observer_location(40.7128, -74.0060)  # New York

# Generate a sky view at a specific time
observation_time = datetime(2024, 6, 15, 22, 0, 0)
simulator.plot_sky(observation_time, save_path='my_sky_view.png')
```

### Create Star Trails

```python
# Show 6 hours of star motion
simulator.create_star_trails(
    start_time=datetime(2024, 6, 15, 20, 0, 0),
    duration_hours=6,
    save_path='star_trails.png'
)
```

### Create Animation

```python
# Animate 2 hours of sky motion
anim = simulator.animate_sky(
    start_time=datetime(2024, 6, 15, 22, 0, 0),
    duration_hours=2,
    interval_minutes=15,
    save_path='sky_animation.gif'
)
```

### Run Demonstrations

```bash
python demo.py
```

This creates comprehensive visualizations showing:
- Multiple locations at the same time
- 24-hour time lapse from one location
- Seasonal sky comparisons

## Generated Files

The simulator generates several types of output:

- **`sky_view.png`** - Static sky view at a specific time
- **`star_trails.png`** - Star paths over multiple hours
- **`sky_animation.gif`** - Animated sky motion
- **`multiple_locations.png`** - Comparison of different locations
- **`time_lapse.png`** - 24-hour progression
- **`seasonal_comparison.png`** - Seasonal variations

## Key Features

### Accurate Astronomical Data
- Uses Hipparcos star catalog with 118,218+ stars
- NASA JPL DE421 ephemeris for planetary positions
- Proper consideration of Earth's rotation and observer location

### Customizable Views
- Filter stars by magnitude (brightness)
- Adjust observation time and duration
- Any geographic location supported
- Polar projection for realistic sky representation

### Visualization Options
- Star size corresponds to brightness (magnitude)
- Altitude-azimuth coordinate system
- Compass directions (N, E, S, W)
- Grid lines for altitude reference

## Dependencies

- `skyfield` - Astronomical calculations
- `numpy` - Numerical operations
- `matplotlib` - Plotting and visualization
- `pandas` - Data handling for star catalog
- `astropy` - Astronomical utilities

## Example Locations

The demo includes these locations:
- New York (40.7°N, 74.0°W)
- London (51.5°N, 0.1°W)
- Sydney (33.9°S, 151.2°E)
- Tokyo (35.7°N, 139.7°E)
- Fairbanks, Alaska (64.2°N, 149.5°W)

## Time Examples

- Equinoxes and solstices for seasonal comparison
- Night hours (18:00-06:00) for best star visibility
- Various times to show Earth's rotation effect

## Technical Details

### Coordinate Systems
- **Input**: ICRS (International Celestial Reference System)
- **Output**: Altitude-Azimuth (horizontal coordinates)
- **Projection**: Polar plot with North at top

### Star Catalog
- Hipparcos catalog with positions, magnitudes, and proper motions
- Filtered by magnitude for performance and clarity
- Brighter stars shown larger in visualizations

### Time Handling
- UTC-based calculations
- Proper Earth rotation calculations
- Account for observer's geographic location

## License

This project uses open-source astronomical data and libraries. Please respect the licenses of all dependencies.