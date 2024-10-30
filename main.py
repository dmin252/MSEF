import streamlit as st
import numpy as np
from thermal_logic import ThermalSimulation
from visualization import HeatingVisualizer
from utils import validate_input, calculate_power_consumption, format_results
from materials_db import MaterialDatabase

def main():
    st.title("Thermal Simulation: Hypocaust vs Modern Heating")
    
    # Initialize material database
    material_db = MaterialDatabase()
    
    # Sidebar for system parameters
    st.sidebar.header("System Parameters")
    
    # Construction Parameters
    with st.sidebar.expander("Construction Parameters", expanded=True):
        # Common parameters
        floor_thickness = st.number_input("Floor Thickness (m)", 0.1, 1.0, 0.2, 0.1)
        wall_thickness = st.number_input("Wall Thickness (m)", 0.1, 1.0, 0.3, 0.1)
        
        # System-specific parameters
        system_type = st.radio("Heating System Type", ["Hypocaust", "Modern"])
        
        if system_type == "Hypocaust":
            pillar_height = st.number_input("Pillar Height (m)", 0.3, 1.0, 0.5, 0.1)
            pillar_spacing = st.number_input("Pillar Spacing (m)", 0.5, 2.0, 1.0, 0.1)
            chamber_height = st.number_input("Underground Chamber Height (m)", 0.3, 1.0, 0.5, 0.1)
            system_params = {
                'pillar_height': pillar_height,
                'pillar_spacing': pillar_spacing,
                'chamber_height': chamber_height
            }
        else:
            radiator_height = st.number_input("Radiator Height (m)", 0.3, 2.0, 1.0, 0.1)
            radiator_width = st.number_input("Radiator Width (m)", 0.3, 2.0, 0.8, 0.1)
            radiator_placement = st.number_input("Radiator Placement Height (m)", 0.1, 2.0, 0.3, 0.1)
            pipe_diameter = st.number_input("Pipe Diameter (mm)", 10.0, 50.0, 15.0, 1.0)
            system_params = {
                'radiator_height': radiator_height,
                'radiator_width': radiator_width,
                'radiator_placement': radiator_placement,
                'pipe_diameter': pipe_diameter / 1000  # Convert to meters
            }

    # Room dimensions in an expander
    with st.sidebar.expander("Room Dimensions", expanded=True):
        room_size = {
            'length': st.number_input("Room Length (m)", 5, 20, 10),
            'width': st.number_input("Room Width (m)", 5, 20, 8),
            'height': st.number_input("Room Height (m)", 2, 5, 3)
        }

    # Energy Source Configuration
    with st.sidebar.expander("Energy Source", expanded=True):
        fuel_type = st.selectbox(
            "Fuel Type",
            ["Wood", "Natural Gas", "Electricity"],
            format_func=lambda x: x.title()
        )
        
        source_temp = st.slider("Heat Source Temperature (°C)", 40, 100, 80)
        
        # Different efficiency ranges based on fuel type
        if fuel_type == "Wood":
            efficiency = st.slider("Combustion Efficiency (%)", 50, 80, 65)
        elif fuel_type == "Natural Gas":
            efficiency = st.slider("Combustion Efficiency (%)", 70, 95, 85)
        else:  # Electricity
            efficiency = st.slider("Conversion Efficiency (%)", 90, 100, 95)
        
        efficiency = efficiency / 100  # Convert to decimal

    # Material Properties
    with st.sidebar.expander("Material Properties", expanded=True):
        # Separate materials by period for the selected system
        ancient_materials = material_db.get_materials_by_period('ancient')
        modern_materials = material_db.get_materials_by_period('modern')
        
        if system_type == "Hypocaust":
            material_choices = ancient_materials['building']
            selected_material = st.selectbox(
                "Select Material",
                list(material_choices.keys()),
                format_func=lambda x: material_choices[x]['name']
            )
            material_props = material_choices[selected_material]
        else:
            material_choices = modern_materials['building']
            selected_material = st.selectbox(
                "Select Material",
                list(material_choices.keys()),
                format_func=lambda x: material_choices[x]['name']
            )
            material_props = material_choices[selected_material]
        
        # Display and allow editing of material properties
        st.write("Material Properties:")
        thermal_conductivity = st.number_input(
            "Thermal Conductivity (W/mK)",
            0.01, 500.0, float(material_props['thermal_conductivity'])
        )
        density = st.number_input(
            "Density (kg/m³)",
            100.0, 10000.0, float(material_props['density'])
        )
        specific_heat = st.number_input(
            "Specific Heat Capacity (J/kgK)",
            100.0, 5000.0, float(material_props['specific_heat'])
        )
        emissivity = st.number_input(
            "Surface Emissivity",
            0.1, 1.0, float(material_props['emissivity'])
        )
        
        # Update material properties
        material_props.update({
            'thermal_conductivity': thermal_conductivity,
            'density': density,
            'specific_heat': specific_heat,
            'emissivity': emissivity
        })

    # Simulation settings in an expander
    with st.sidebar.expander("Simulation Settings", expanded=True):
        time_steps = st.slider("Simulation Time Steps", 50, 200, 100)
        initial_temp = st.slider("Initial Temperature (°C)", 0, 30, 15)

    # Run simulation button
    if st.sidebar.button('Run Simulation'):
        # Update material properties with energy source settings
        material_props.update({
            'source_temp': source_temp,
            'efficiency': efficiency,
            'fuel_type': fuel_type.lower()
        })
        
        # Create simulation instance with updated parameters
        sim = ThermalSimulation(
            (room_size['length'], room_size['width']),
            material_props,
            system_type=system_type.lower()
        )
        
        # Update system-specific parameters
        sim.update_system_params(system_params)
        
        # Calculate temperature distribution
        temp_distribution = sim.calculate_heat_transfer(initial_temp, time_steps)
        metrics = sim.calculate_efficiency(temp_distribution)
        
        # Create visualizer
        visualizer = HeatingVisualizer()
        
        # Display system diagram
        st.subheader(f"{system_type} System Diagram")
        st.image(visualizer.create_system_diagram(system_type.lower()))
        
        # Display temperature distribution
        st.subheader("Heat Distribution")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("2D Heat Map")
            st.pyplot(visualizer.create_heatmap(temp_distribution))
            
        with col2:
            st.write("3D Visualization")
            st.plotly_chart(visualizer.create_3d_heatmap(
                temp_distribution,
                (room_size['length'], room_size['width'])
            ))
        
        # Display metrics
        st.subheader("System Performance")
        formatted_metrics = format_results(metrics)
        for key, value in formatted_metrics.items():
            st.write(f"- {key.title()}: {value}")
        
        # Energy Retention Analysis
        st.header("Energy Retention Analysis")
        hours, retention = sim.calculate_hourly_energy_retention(initial_temp)
        
        # Create and display energy retention plot
        retention_plot = visualizer.create_energy_retention_plot(
            hours, retention, retention  # Using same data for comparison (will be different in actual simulation)
        )
        st.plotly_chart(retention_plot)
        
        # Calculate and display power consumption
        volume = room_size['length'] * room_size['width'] * room_size['height']
        temp_diff = source_temp - initial_temp
        power_consumption = calculate_power_consumption(volume, temp_diff, metrics['efficiency'])
        
        st.subheader("Power Consumption")
        st.write(f"Estimated Power Consumption: {power_consumption:.2f} kWh")
        
        # Calculate and display emissions
        emissions = sim.calculate_co2_emissions(power_consumption, 24)  # 24-hour period
        st.subheader("Environmental Impact")
        for source, value in emissions.items():
            st.write(f"CO2 Emissions ({source.title()}): {value:.2f} kg")

if __name__ == "__main__":
    main()
