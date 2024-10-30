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
    
    # Room dimensions in an expander
    with st.sidebar.expander("Room Dimensions", expanded=True):
        room_size = {
            'length': st.number_input("Room Length (m)", 5, 20, 10),
            'width': st.number_input("Room Width (m)", 5, 20, 8),
            'height': st.number_input("Room Height (m)", 2, 5, 3)
        }

    # Material selection in an expander
    with st.sidebar.expander("Material Properties", expanded=True):
        # Separate materials by period for the selected system
        ancient_materials = material_db.get_materials_by_period('ancient')
        modern_materials = material_db.get_materials_by_period('modern')
        
        # Create lists of material names for dropdowns
        ancient_building_materials = list(ancient_materials['building'].keys())
        modern_building_materials = list(modern_materials['building'].keys())
        
        # Material selection dropdowns
        hypocaust_material = st.selectbox(
            "Hypocaust System Material",
            ancient_building_materials,
            index=0
        )
        modern_material = st.selectbox(
            "Modern System Material",
            modern_building_materials,
            index=0
        )
        
        # Display selected material properties
        hypocaust_props = material_db.get_building_material(hypocaust_material)
        modern_props = material_db.get_building_material(modern_material)
        
        if hypocaust_props and modern_props:
            cols = st.columns(2)
            with cols[0]:
                st.write("Hypocaust Material:")
                st.write(f"- Conductivity: {hypocaust_props['thermal_conductivity']} W/mK")
                st.write(f"- Resistance: {hypocaust_props['thermal_resistance']} m²K/W")
            with cols[1]:
                st.write("Modern Material:")
                st.write(f"- Conductivity: {modern_props['thermal_conductivity']} W/mK")
                st.write(f"- Resistance: {modern_props['thermal_resistance']} m²K/W")

    # Simulation settings in an expander
    with st.sidebar.expander("Simulation Settings", expanded=True):
        time_steps = st.slider("Simulation Time Steps", 50, 200, 100)
        initial_temp = st.slider("Initial Temperature (°C)", 0, 30, 15)
        source_temp = st.slider("Heat Source Temperature (°C)", 40, 100, 80)

    # Run simulation button
    if st.sidebar.button('Run Simulation'):
        # Get material properties for simulations
        hypocaust_props = material_db.get_building_material(hypocaust_material).copy()
        modern_props = material_db.get_building_material(modern_material).copy()
        
        # Add source temperature to properties
        hypocaust_props['source_temp'] = source_temp
        modern_props['source_temp'] = source_temp

        # Create simulation instances
        hypocaust_sim = ThermalSimulation(
            (room_size['length'], room_size['width']),
            hypocaust_props,
            system_type='hypocaust'
        )
        modern_sim = ThermalSimulation(
            (room_size['length'], room_size['width']),
            modern_props,
            system_type='modern'
        )

        # Run simulations and get results
        hypocaust_temp = hypocaust_sim.calculate_heat_transfer(initial_temp, time_steps)
        modern_temp = modern_sim.calculate_heat_transfer(initial_temp, time_steps)
        
        # Get time series data
        hypocaust_time_series = hypocaust_sim.get_time_series_data()
        modern_time_series = modern_sim.get_time_series_data()
        
        # Create visualizer
        visualizer = HeatingVisualizer()
        
        # Time Series Analysis Section
        st.header("Time Series Analysis")
        
        # Plot time series data
        st.plotly_chart(
            visualizer.create_time_series_plot(
                hypocaust_time_series,
                modern_time_series
            ),
            use_container_width=True
        )
        
        # Plot efficiency radar chart using latest data
        st.plotly_chart(
            visualizer.create_efficiency_radar_plot(
                hypocaust_time_series[-1],
                modern_time_series[-1]
            ),
            use_container_width=True
        )
        
        # System Comparisons
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Hypocaust System")
            hypocaust_metrics = hypocaust_sim.calculate_efficiency(hypocaust_temp)
            
            # System diagram
            st.image(visualizer.create_system_diagram('hypocaust'))
            
            # 2D heatmap
            st.subheader("2D Heat Distribution")
            st.pyplot(visualizer.create_heatmap(hypocaust_temp))
            
            # 3D visualization
            st.subheader("3D Heat Distribution")
            st.plotly_chart(visualizer.create_3d_heatmap(
                hypocaust_temp, 
                (room_size['length'], room_size['width'])
            ))
            
            # Metrics
            st.write("Final Metrics:")
            hypocaust_formatted = format_results(hypocaust_metrics)
            for key, value in hypocaust_formatted.items():
                st.write(f"- {key.title()}: {value}")

        with col2:
            st.subheader("Modern Heating System")
            modern_metrics = modern_sim.calculate_efficiency(modern_temp)
            
            # System diagram
            st.image(visualizer.create_system_diagram('modern'))
            
            # 2D heatmap
            st.subheader("2D Heat Distribution")
            st.pyplot(visualizer.create_heatmap(modern_temp))
            
            # 3D visualization
            st.subheader("3D Heat Distribution")
            st.plotly_chart(visualizer.create_3d_heatmap(
                modern_temp,
                (room_size['length'], room_size['width'])
            ))
            
            # Metrics
            st.write("Final Metrics:")
            modern_formatted = format_results(modern_metrics)
            for key, value in modern_formatted.items():
                st.write(f"- {key.title()}: {value}")

        # Environmental Impact Analysis
        st.header("Environmental Impact")
        
        volume = room_size['length'] * room_size['width'] * room_size['height']
        temp_diff = source_temp - initial_temp
        
        # Calculate power consumption using final efficiency
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
        cols = st.columns(2)
        
        with cols[0]:
            st.write("Hypocaust System:")
            for source, value in hypocaust_emissions.items():
                st.write(f"- {source.title()}: {value:.2f} kg CO2")
                
        with cols[1]:
            st.write("Modern System:")
            for source, value in modern_emissions.items():
                st.write(f"- {source.title()}: {value:.2f} kg CO2")

if __name__ == "__main__":
    main()
