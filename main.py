import streamlit as st
import numpy as np
from thermal_logic import ThermalSimulation
from visualization import HeatingVisualizer
from utils import validate_input, calculate_power_consumption, format_results

def main():
    st.title("Thermal Simulation: Hypocaust vs Modern Heating")
    st.sidebar.header("System Parameters")

    # User inputs
    room_size = {
        'length': st.sidebar.slider("Room Length (m)", 5, 20, 10),
        'width': st.sidebar.slider("Room Width (m)", 5, 20, 8),
        'height': st.sidebar.slider("Room Height (m)", 2, 5, 3)
    }

    material_properties = {
        'thermal_conductivity': st.sidebar.slider("Thermal Conductivity (W/mK)", 0.1, 2.0, 0.5),
        'specific_heat': st.sidebar.slider("Specific Heat (J/kgK)", 800, 2000, 1000),
        'density': st.sidebar.slider("Density (kg/m³)", 1000, 3000, 1500),
    }

    # Calculate derived properties
    material_properties['thermal_diffusivity'] = (
        material_properties['thermal_conductivity'] /
        (material_properties['density'] * material_properties['specific_heat'])
    )
    material_properties['source_temp'] = 80  # °C

    # Create simulation instances
    hypocaust_sim = ThermalSimulation(
        (room_size['length'], room_size['width']),
        material_properties
    )
    modern_sim = ThermalSimulation(
        (room_size['length'], room_size['width']),
        material_properties
    )

    # Run simulations
    initial_temp = 15  # °C
    time_steps = 100

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Hypocaust System")
        hypocaust_temp = hypocaust_sim.calculate_heat_transfer(initial_temp, time_steps)
        hypocaust_metrics = hypocaust_sim.calculate_efficiency(hypocaust_temp)
        
        # Visualization
        visualizer = HeatingVisualizer()
        st.image(visualizer.create_system_diagram('hypocaust'))
        st.pyplot(visualizer.create_heatmap(hypocaust_temp))
        
        # Metrics
        st.write("System Metrics:")
        hypocaust_formatted = format_results(hypocaust_metrics)
        for key, value in hypocaust_formatted.items():
            st.write(f"- {key.title()}: {value}")

    with col2:
        st.subheader("Modern Heating System")
        modern_temp = modern_sim.calculate_heat_transfer(initial_temp, time_steps)
        modern_metrics = modern_sim.calculate_efficiency(modern_temp)
        
        # Visualization
        st.image(visualizer.create_system_diagram('modern'))
        st.pyplot(visualizer.create_heatmap(modern_temp))
        
        # Metrics
        st.write("System Metrics:")
        modern_formatted = format_results(modern_metrics)
        for key, value in modern_formatted.items():
            st.write(f"- {key.title()}: {value}")

    # CO2 Emissions Comparison
    st.header("Environmental Impact")
    
    volume = room_size['length'] * room_size['width'] * room_size['height']
    temp_diff = material_properties['source_temp'] - initial_temp
    
    power_hypocaust = calculate_power_consumption(
        volume, temp_diff, hypocaust_metrics['efficiency']
    )
    power_modern = calculate_power_consumption(
        volume, temp_diff, modern_metrics['efficiency']
    )
    
    # Calculate emissions
    duration = 24  # hours
    hypocaust_emissions = hypocaust_sim.calculate_co2_emissions(power_hypocaust, duration)
    modern_emissions = modern_sim.calculate_co2_emissions(power_modern, duration)
    
    # Display emissions comparison
    st.subheader("Daily CO2 Emissions (kg)")
    emissions_data = {
        'Hypocaust': hypocaust_emissions,
        'Modern': modern_emissions
    }
    
    for system, emissions in emissions_data.items():
        st.write(f"\n{system} System:")
        for source, value in emissions.items():
            st.write(f"- {source.title()}: {value:.2f} kg CO2")

if __name__ == "__main__":
    main()
