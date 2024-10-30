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
