import numpy as np
from scipy.integrate import odeint

class ThermalSimulation:
    def __init__(self, room_dimensions, material_properties, system_type='modern'):
        """Initialize thermal simulation with error handling for properties"""
        self.dimensions = room_dimensions
        
        # Verify required properties
        required_props = ['thermal_conductivity', 'density', 'specific_heat']
        missing_props = [prop for prop in required_props if prop not in material_properties]
        if missing_props:
            raise ValueError(f"Missing required material properties: {', '.join(missing_props)}")
        
        # Create a copy of properties and calculate thermal diffusivity if not provided
        self.properties = material_properties.copy()
        if 'thermal_diffusivity' not in self.properties:
            self.properties['thermal_diffusivity'] = (
                self.properties['thermal_conductivity'] / 
                (self.properties['density'] * self.properties['specific_heat'])
            )
        
        self.system_type = system_type
        self.grid_size = (50, 50)
        
    def calculate_heat_transfer(self, initial_temp, time_steps):
        """Calculate heat transfer using finite difference method"""
        dx, dy = self.dimensions[0]/self.grid_size[0], self.dimensions[1]/self.grid_size[1]
        alpha = self.properties['thermal_diffusivity']
        dt = 0.25 * min(dx, dy)**2 / alpha
        
        # Initialize temperature grid based on system type
        T = np.ones(self.grid_size) * initial_temp
        
        # Apply boundary conditions based on system type
        if self.system_type == 'hypocaust':
            # Multiple heat sources from floor with pillar conduction
            pillar_positions = range(0, self.grid_size[0], 5)
            for x in pillar_positions:
                # Heat source at floor
                T[-1, x] = self.properties['source_temp']
                # Pillar heat conduction
                T[-10:, x] = np.linspace(initial_temp, self.properties['source_temp'], 10)
        else:
            # Modern system: Single concentrated heat source from wall
            wall_center = self.grid_size[1] // 2
            radiator_height = self.grid_size[0] // 3
            T[radiator_height:2*radiator_height, 0:2] = self.properties['source_temp']
        
        # Time evolution with improved physics
        for t in range(time_steps):
            T_new = T.copy()
            for i in range(1, self.grid_size[0]-1):
                for j in range(1, self.grid_size[1]-1):
                    # Enhanced heat transfer calculation
                    if self.system_type == 'hypocaust':
                        # Add vertical convection for hypocaust
                        convection_factor = 1.5 if i < self.grid_size[0]-1 else 1.0
                        T_new[i,j] = T[i,j] + alpha * dt * (
                            convection_factor * (T[i+1,j] - 2*T[i,j] + T[i-1,j])/dx**2 +
                            (T[i,j+1] - 2*T[i,j] + T[i,j-1])/dy**2
                        )
                    else:
                        # Add horizontal convection for modern system
                        convection_factor = 1.5 if j > 0 else 1.0
                        T_new[i,j] = T[i,j] + alpha * dt * (
                            (T[i+1,j] - 2*T[i,j] + T[i-1,j])/dx**2 +
                            convection_factor * (T[i,j+1] - 2*T[i,j] + T[i,j-1])/dy**2
                        )
            T = T_new
            
        return T
    
    def calculate_efficiency(self, temperature_distribution):
        """Calculate heating system efficiency"""
        mean_temp = np.mean(temperature_distribution)
        temp_uniformity = 1 - np.std(temperature_distribution)/mean_temp
        
        # Adjust efficiency calculation based on system type
        system_factor = 0.9 if self.system_type == 'hypocaust' else 1.0  # Modern systems are typically more efficient
        
        return {
            'mean_temperature': mean_temp,
            'uniformity': temp_uniformity,
            'efficiency': system_factor * temp_uniformity * (mean_temp/self.properties['source_temp'])
        }
    
    def calculate_co2_emissions(self, power_consumption, duration):
        """Calculate CO2 emissions based on power consumption"""
        # Average CO2 emissions per kWh (varies by energy source)
        co2_per_kwh = {
            'natural_gas': 0.2,
            'electricity': 0.5,
            'wood': 0.1
        }
        
        return {
            source: power_consumption * co2_per_kwh[source] * duration 
            for source in co2_per_kwh
        }

    def calculate_hourly_energy_retention(self, initial_temp, duration_hours=24):
        """Calculate hourly energy retention over specified duration"""
        # Input validation
        if initial_temp < -50 or initial_temp > 100:
            raise ValueError("Initial temperature must be between -50°C and 100°C")
        if duration_hours <= 0:
            raise ValueError("Duration must be positive")
        if 'source_temp' not in self.properties:
            raise ValueError("Source temperature not specified in properties")
            
        # Calculate room volume and validate dimensions
        length, width = self.dimensions
        if length <= 0 or width <= 0:
            raise ValueError("Room dimensions must be positive")
        
        # Calculate room volume and surface area
        height = 3.0  # Standard room height in meters
        volume = length * width * height
        surface_area = 2 * (length * width + length * height + width * height)
        
        # Calculate thermal mass
        thermal_mass = volume * self.properties['density'] * self.properties['specific_heat']
        
        # Initialize arrays
        time_hours = np.arange(duration_hours + 1)
        energy_retention = np.zeros(duration_hours + 1)
        energy_retention[0] = 100.0  # Start at 100%
        
        # Calculate heat loss coefficient (U-value)
        u_value = self.properties['thermal_conductivity'] / 0.2  # Assuming 0.2m wall thickness
        
        # System-specific factors
        if self.system_type == 'hypocaust':
            thermal_mass_factor = 1.5  # Higher thermal mass effect
            insulation_factor = 0.7   # Better insulation due to thick walls
        else:
            thermal_mass_factor = 1.0  # Standard thermal mass
            insulation_factor = 1.0   # Standard insulation
            
        # Calculate heat loss rate without scaling factor
        base_loss_rate = (u_value * surface_area) / (thermal_mass * thermal_mass_factor)
        loss_rate = base_loss_rate * insulation_factor
        
        print(f"Debug - System parameters:")
        print(f"Volume: {volume:.2f} m³")
        print(f"Surface area: {surface_area:.2f} m²")
        print(f"Thermal mass: {thermal_mass:.2f} J/K")
        print(f"U-value: {u_value:.4f} W/m²K")
        print(f"System type: {self.system_type}")
        print(f"Base loss rate: {base_loss_rate:.6f}")
        print(f"Final loss rate: {loss_rate:.6f}")
        
        # Calculate retention curve using exponential decay
        for hour in range(1, duration_hours + 1):
            retention = 100 * np.exp(-loss_rate * hour)
            # Ensure retention stays within physical limits
            retention = max(20, min(100, retention))  # Minimum 20% retention
            energy_retention[hour] = retention
            
        print(f"Initial retention: {energy_retention[0]:.1f}%")
        print(f"Final retention: {energy_retention[-1]:.1f}%")
            
        return time_hours, energy_retention
