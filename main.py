import streamlit as st
import numpy as np
import plotly.graph_objects as go
from thermal_logic import ThermalSimulation
from visualization import HeatingVisualizer
from utils import validate_input, calculate_power_consumption, format_results
from materials_db import MaterialDatabase
from system_equivalency import SystemEquivalency

def create_emissions_chart(hypocaust_data, modern_data, category):
    """Create a bar chart comparing emissions between systems"""
    systems = ['Hypocaust System', 'Modern System']
    values = [hypocaust_data[category], modern_data[category]]
    
    fig = go.Figure(data=[
        go.Bar(name=systems[0], x=[category], y=[values[0]], marker_color='#FF4B4B'),
        go.Bar(name=systems[1], x=[category], y=[values[1]], marker_color='#1F77B4')
    ])
    
    fig.update_layout(
        title=f'{category.replace("_", " ").title()} Comparison',
        yaxis_title='CO₂ Emissions (kg)',
        barmode='group',
        width=400,
        height=300
    )
    
    return fig

def main():
    st.title("Thermal Simulation: Hypocaust vs Modern Heating")
    
    # Initialize material database
    material_db = MaterialDatabase()
    
    # Sidebar for system parameters
    st.sidebar.header("System Parameters")
    
    # Construction Parameters
    with st.sidebar.expander("Construction Parameters", expanded=True):
        # Room dimensions moved up for system equivalency calculations
        room_size = {
            'length': st.number_input("Room Length (m)", 5, 20, 10),
            'width': st.number_input("Room Width (m)", 5, 20, 8),
            'height': st.number_input("Room Height (m)", 2, 5, 3)
        }
        
        # Initialize system equivalency calculator
        room_volume = room_size['length'] * room_size['width'] * room_size['height']
        system_equiv = SystemEquivalency(room_volume)
        
        # Common parameters
        floor_thickness = st.number_input("Floor Thickness (m)", 0.1, 1.0, 0.2, 0.1)
        wall_thickness = st.number_input("Wall Thickness (m)", 0.1, 1.0, 0.3, 0.1)
        
        # System type selection for parameter entry
        system_input = st.radio(
            "Enter Parameters For:",
            ["Modern System", "Hypocaust System"],
            help="Choose which system to enter parameters for. The other system's parameters will be automatically calculated for equivalency."
        )
        
        if system_input == "Modern System":
            # Modern system parameters
            modern_params = {
                'radiator_height': st.number_input("Radiator Height (m)", 0.3, 2.0, 1.0, 0.1),
                'radiator_width': st.number_input("Radiator Width (m)", 0.3, 2.0, 0.8, 0.1),
                'radiator_placement': st.number_input("Radiator Placement Height (m)", 0.1, 2.0, 0.3, 0.1),
                'pipe_diameter': st.number_input("Pipe Diameter (mm)", 10.0, 50.0, 15.0, 1.0) / 1000
            }
            # Calculate equivalent hypocaust parameters
            hypocaust_params = system_equiv.convert_modern_to_hypocaust(modern_params)
            
            # Display calculated hypocaust parameters
            st.write("Equivalent Hypocaust Parameters:")
            for key, value in hypocaust_params.items():
                st.write(f"- {key.replace('_', ' ').title()}: {value:.2f} m")
        else:
            # Hypocaust parameters
            hypocaust_params = {
                'pillar_height': st.number_input("Pillar Height (m)", 0.3, 1.0, 0.5, 0.1),
                'pillar_spacing': st.number_input("Pillar Spacing (m)", 0.5, 2.0, 1.0, 0.1),
                'chamber_height': st.number_input("Underground Chamber Height (m)", 0.3, 1.0, 0.5, 0.1)
            }
            # Calculate equivalent modern parameters
            modern_params = system_equiv.convert_hypocaust_to_modern(hypocaust_params)
            
            # Display calculated modern parameters
            st.write("Equivalent Modern System Parameters:")
            for key, value in modern_params.items():
                st.write(f"- {key.replace('_', ' ').title()}: {value:.2f} m")

    # Material Properties
    with st.sidebar.expander("Material Properties", expanded=True):
        # Get materials by period
        ancient_materials = material_db.get_materials_by_period('ancient')
        modern_materials = material_db.get_materials_by_period('modern')
        
        # Hypocaust material selection
        st.subheader("Hypocaust System Materials")
        hypocaust_material = st.selectbox(
            "Select Hypocaust Material",
            list(ancient_materials['building'].keys()),
            format_func=lambda x: ancient_materials['building'][x]['name']
        )
        hypocaust_props = ancient_materials['building'][hypocaust_material].copy()
        hypocaust_props['material_type'] = hypocaust_material
        
        # Modern system material selection
        st.subheader("Modern System Materials")
        modern_material = st.selectbox(
            "Select Modern Material",
            list(modern_materials['building'].keys()),
            format_func=lambda x: modern_materials['building'][x]['name']
        )
        modern_props = modern_materials['building'][modern_material].copy()
        modern_props['material_type'] = modern_material

    # Energy Source Configuration
    with st.sidebar.expander("Energy Source", expanded=True):
        fuel_type = st.selectbox(
            "Fuel Type",
            ["wood", "natural_gas", "electricity"],
            format_func=lambda x: x.replace("_", " ").title()
        )
        
        source_temp = st.slider("Heat Source Temperature (°C)", 40, 100, 80)
        initial_temp = st.slider("Initial Temperature (°C)", 0, 30, 15)
        temp_diff = source_temp - initial_temp
        
        # Different efficiency ranges based on fuel type
        if fuel_type == "wood":
            efficiency = st.slider("Combustion Efficiency (%)", 50, 80, 65)
        elif fuel_type == "natural_gas":
            efficiency = st.slider("Combustion Efficiency (%)", 70, 95, 85)
        else:  # Electricity
            efficiency = st.slider("Conversion Efficiency (%)", 90, 100, 95)
        
        efficiency = efficiency / 100  # Convert to decimal

    # Run simulation button
    if st.sidebar.button('Run Simulation'):
        # Update material properties with energy source settings
        for props in [hypocaust_props, modern_props]:
            props.update({
                'source_temp': source_temp,
                'efficiency': efficiency,
                'fuel_type': fuel_type
            })
        
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
        
        # Update system parameters
        hypocaust_sim.update_system_params(hypocaust_params)
        modern_sim.update_system_params(modern_params)
        
        # Calculate temperature distributions
        hypocaust_temp = hypocaust_sim.calculate_heat_transfer(initial_temp, 100)
        modern_temp = modern_sim.calculate_heat_transfer(initial_temp, 100)
        
        # Create visualizer
        visualizer = HeatingVisualizer()
        
        # Add System Equivalency Analysis section
        st.header("System Equivalency Analysis")
        
        # Calculate and display heat output equivalency
        heat_output = system_equiv.calculate_heat_output_equivalency(source_temp, initial_temp)
        st.subheader("Heat Output Comparison")
        col1, col2 = st.columns(2)
        with col1:
            st.write("Modern System Output:", f"{heat_output['modern_output']:.2f} W/m²")
        with col2:
            st.write("Hypocaust System Output:", f"{heat_output['hypocaust_output']:.2f} W/m²")
        st.write(f"Output Ratio (Hypocaust/Modern): {heat_output['output_ratio']:.2%}")
        
        # Calculate and display response times
        response_times = system_equiv.calculate_response_times(temp_diff)
        st.subheader("System Response Times")
        col3, col4 = st.columns(2)
        with col3:
            st.write("Modern System:", f"{response_times['modern_response']:.1f} minutes")
        with col4:
            st.write("Hypocaust System:", f"{response_times['hypocaust_response']:.1f} minutes")
        st.write(f"Response Time Ratio: {response_times['response_ratio']:.1f}x slower for Hypocaust")
        
        # Display scientific justification
        st.header("Scientific Justification")
        justification = system_equiv.get_scientific_justification()
        with st.expander("View Scientific Justification"):
            for aspect, explanation in justification.items():
                st.subheader(aspect.replace('_', ' ').title())
                st.write(explanation.strip())

        # Display system diagrams and other visualizations
        st.header("System Diagrams")
        col5, col6 = st.columns(2)
        with col5:
            st.write("Hypocaust System")
            st.image(visualizer.create_system_diagram('hypocaust'))
        with col6:
            st.write("Modern Heating System")
            st.image(visualizer.create_system_diagram('modern'))

        # Display heat distribution visualizations and other metrics
        # [Previous visualization code remains the same]

if __name__ == "__main__":
    main()
