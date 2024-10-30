import numpy as np
from scipy.integrate import odeint
from datetime import datetime, timedelta

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
        
    def update_system_params(self, params):
        """Update system-specific parameters"""
        self.system_params = params
        
        # Update grid initialization based on system parameters
        if self.system_type == 'hypocaust':
            self.pillar_height = params['pillar_height']
            self.pillar_spacing = params['pillar_spacing']
            self.chamber_height = params['chamber_height']
        else:
            self.radiator_height = params['radiator_height']
            self.radiator_width = params['radiator_width']
            self.radiator_placement = params['radiator_placement']
            self.pipe_diameter = params['pipe_diameter']
        
    def calculate_heat_transfer(self, initial_temp, time_steps):
        """Calculate heat transfer using finite difference method"""
        dx, dy = self.dimensions[0]/self.grid_size[0], self.dimensions[1]/self.grid_size[1]
        alpha = self.properties['thermal_diffusivity']
        dt = 0.25 * min(dx, dy)**2 / alpha
        
        # Initialize temperature grid based on system type
        T = np.ones(self.grid_size) * initial_temp
        
        # Apply boundary conditions based on system type
        if self.system_type == 'hypocaust':
            # Calculate pillar positions based on spacing
            pillar_spacing_cells = int(self.pillar_spacing * self.grid_size[0] / self.dimensions[0])
            pillar_positions = range(0, self.grid_size[0], pillar_spacing_cells)
            
            for x in pillar_positions:
                # Heat source at floor with actual chamber height
                chamber_cells = int(self.chamber_height * self.grid_size[1] / self.dimensions[1])
                T[-chamber_cells:, x] = self.properties['source_temp']
                
                # Pillar heat conduction with actual height
                pillar_cells = int(self.pillar_height * self.grid_size[1] / self.dimensions[1])
                T[-pillar_cells:, x] = np.linspace(initial_temp, self.properties['source_temp'], pillar_cells)
        else:
            # Modern system with actual radiator dimensions
            radiator_height_cells = int(self.radiator_height * self.grid_size[0] / self.dimensions[0])
            radiator_width_cells = max(1, int(self.radiator_width * self.grid_size[1] / self.dimensions[1]))
            placement_cells = int(self.radiator_placement * self.grid_size[0] / self.dimensions[0])
            
            T[placement_cells:placement_cells+radiator_height_cells, 0:radiator_width_cells] = self.properties['source_temp']
        
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

    def calculate_embodied_carbon(self, material_volume):
        """Calculate embodied carbon based on material type and volume"""
        # Embodied carbon factors (kgCO2e/m³)
        embodied_carbon_factors = {
            'roman_concrete': 95,  # Lower due to natural materials
            'roman_brick': 150,
            'tuff_stone': 70,
            'marble': 180,
            'concrete': 350,  # Higher due to cement content
            'brick': 280,
            'mineral_wool': 45,
            'steel': 12500,  # For radiators
            'copper': 7850   # For pipes
        }
        
        material_type = self.properties.get('material_type', 'concrete')
        carbon_factor = embodied_carbon_factors.get(material_type, 200)  # Default factor
        
        return carbon_factor * material_volume

    def calculate_maintenance_impact(self, lifespan_years):
        """Calculate environmental impact of maintenance over system lifespan"""
        # Annual maintenance factors (kgCO2e/year)
        if self.system_type == 'hypocaust':
            annual_maintenance = {
                'cleaning': 5,
                'repairs': 15,
                'material_replacement': 10
            }
        else:
            annual_maintenance = {
                'cleaning': 2,
                'repairs': 25,
                'part_replacement': 20,
                'fluid_replacement': 8
            }
        
        total_maintenance = sum(annual_maintenance.values()) * lifespan_years
        return total_maintenance

    def calculate_co2_emissions(self, power_consumption, duration_hours):
        """Calculate comprehensive CO2 emissions including lifecycle analysis"""
        # Base emissions from energy source
        emissions_factors = {
            'natural_gas': 0.2,  # kgCO2/kWh
            'electricity': 0.5,
            'wood': 0.1
        }
        
        # Get the fuel type and its emission factor
        fuel_type = self.properties.get('fuel_type', 'natural_gas')
        emission_factor = emissions_factors.get(fuel_type, 0.2)
        
        # Calculate operational emissions
        operational_emissions = power_consumption * emission_factor * duration_hours
        
        # Calculate system volume for embodied carbon
        if self.system_type == 'hypocaust':
            system_volume = (self.dimensions[0] * self.dimensions[1] * self.chamber_height +
                           self.pillar_height * 0.2 * 0.2 * (self.dimensions[0] / self.pillar_spacing))
        else:
            system_volume = (self.radiator_height * self.radiator_width * 0.1 +
                           np.pi * (self.pipe_diameter/2)**2 * (self.dimensions[0] + self.dimensions[1]))
        
        # Calculate embodied carbon
        embodied_carbon = self.calculate_embodied_carbon(system_volume)
        
        # Calculate maintenance impact (assuming 1 year of operation)
        maintenance_impact = self.calculate_maintenance_impact(1)
        
        # Calculate potential carbon offsets
        if self.system_type == 'hypocaust':
            # Thermal mass benefits and natural ventilation
            offset_factor = 0.15
        else:
            # Modern control systems and energy recovery
            offset_factor = 0.1
        
        carbon_offset = operational_emissions * offset_factor
        
        # Return detailed emissions breakdown
        return {
            'operational': {
                source: operational_emissions * (0.8 if source == fuel_type else 0.1)
                for source in emissions_factors.keys()
            },
            'embodied_carbon': embodied_carbon,
            'maintenance_impact': maintenance_impact,
            'carbon_offset': carbon_offset,
            'net_emissions': operational_emissions + embodied_carbon + maintenance_impact - carbon_offset
        }

    def calculate_hourly_energy_retention(self, initial_temp, duration_hours=24):
        """Calculate hourly energy retention with sinusoidal pattern and random variation"""
        hours = duration_hours + 1
        time_points = np.arange(hours)
        
        # Generate retention data based on system type
        if self.system_type == 'hypocaust':
            # Higher baseline (85%) with smaller variation (±10%)
            retention = 85 + 10 * np.sin(np.linspace(0, 2*np.pi, hours)) + \
                       np.random.normal(0, 2, hours)
        else:
            # Lower baseline (75%) with larger variation (±15%)
            retention = 75 + 15 * np.sin(np.linspace(0, 2*np.pi, hours)) + \
                       np.random.normal(0, 2, hours)
        
        # Ensure retention stays within physical limits
        retention = np.clip(retention, 20, 100)
        
        return time_points, retention
