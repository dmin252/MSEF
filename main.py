import streamlit as st
import numpy as np
import plotly.graph_objects as go
from thermal_logic import ThermalSimulation
from visualization import HeatingVisualizer
from utils import validate_input, calculate_power_consumption, format_results
from materials_db import MaterialDatabase
from system_equivalency import SystemEquivalency
import traceback

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
        width=800,
        height=400
    )
    
    return fig

def main():
    st.set_page_config(layout="wide")
    st.title("Thermal Simulation: Hypocaust vs Modern Heating")
    
    # Initialize material database
    material_db = MaterialDatabase()
    
    # Sidebar for system parameters
    st.sidebar.header("System Parameters")
    
    # Construction Parameters
    with st.sidebar.expander("Construction Parameters"):
        # Room dimensions
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
            modern_params = {
                'radiator_height': st.number_input("Radiator Height (m)", 0.3, 2.0, 1.0, 0.1),
                'radiator_width': st.number_input("Radiator Width (m)", 0.3, 2.0, 0.8, 0.1),
                'radiator_placement': st.number_input("Radiator Placement Height (m)", 0.1, 2.0, 0.3, 0.1),
                'pipe_diameter': st.number_input("Pipe Diameter (mm)", 10.0, 50.0, 15.0, 1.0) / 1000
            }
            hypocaust_params = system_equiv.convert_modern_to_hypocaust(modern_params)
        else:
            hypocaust_params = {
                'pillar_height': st.number_input("Pillar Height (m)", 0.3, 1.0, 0.5, 0.1),
                'pillar_spacing': st.number_input("Pillar Spacing (m)", 0.5, 2.0, 1.0, 0.1),
                'chamber_height': st.number_input("Underground Chamber Height (m)", 0.3, 1.0, 0.5, 0.1)
            }
            modern_params = system_equiv.convert_hypocaust_to_modern(hypocaust_params)

    # Display equivalent parameters outside the expander
    st.sidebar.markdown("---")
    col1, col2 = st.sidebar.columns(2)
    if system_input == "Modern System":
        with col1:
            st.write("Equivalent Hypocaust Parameters")
            for key, value in hypocaust_params.items():
                st.write(f"- {key.replace('_', ' ').title()}: {value:.2f} m")
    else:
        with col2:
            st.write("Equivalent Modern Parameters")
            for key, value in modern_params.items():
                st.write(f"- {key.replace('_', ' ').title()}: {value:.2f} m")

    # Material Properties
    with st.sidebar.expander("Material Properties"):
        ancient_materials = material_db.get_materials_by_period('ancient')
        modern_materials = material_db.get_materials_by_period('modern')
        
        st.subheader("Hypocaust System Materials")
        hypocaust_material = st.selectbox(
            "Select Hypocaust Material",
            list(ancient_materials['building'].keys()),
            format_func=lambda x: ancient_materials['building'][x]['name'],
            help="Historical Roman building materials used in hypocaust construction"
        )
        hypocaust_props = ancient_materials['building'][hypocaust_material].copy()
        hypocaust_props['material_type'] = hypocaust_material
        
        st.subheader("Modern System Materials")
        modern_material = st.selectbox(
            "Select Modern Material",
            list(modern_materials['building'].keys()),
            format_func=lambda x: modern_materials['building'][x]['name'],
            help="Contemporary building materials used in modern heating systems"
        )
        modern_props = modern_materials['building'][modern_material].copy()
        modern_props['material_type'] = modern_material

    # Energy Source Configuration
    with st.sidebar.expander("Energy Source"):
        fuel_type = st.selectbox(
            "Fuel Type",
            ["wood", "natural_gas", "electricity"],
            format_func=lambda x: x.replace("_", " ").title(),
            help="Select the primary energy source for the heating system"
        )
        
        source_temp = st.slider(
            "Heat Source Temperature (°C)", 
            40, 100, 80,
            help="Temperature of the heat source (furnace or boiler)"
        )
        initial_temp = st.slider(
            "Initial Temperature (°C)", 
            0, 30, 15,
            help="Starting room temperature before heating"
        )
        temp_diff = source_temp - initial_temp
        
        if fuel_type == "wood":
            efficiency = st.slider("Combustion Efficiency (%)", 50, 80, 65)
        elif fuel_type == "natural_gas":
            efficiency = st.slider("Combustion Efficiency (%)", 70, 95, 85)
        else:  # Electricity
            efficiency = st.slider("Conversion Efficiency (%)", 90, 100, 95)
        
        efficiency = efficiency / 100

    # Run simulation button
    if st.sidebar.button('Run Simulation'):
        # Create containers for progress tracking
        progress_container = st.empty()
        status_container = st.empty()
        error_container = st.empty()
        
        try:
            # Update material properties
            progress_container.progress(0)
            status_container.info("Initializing simulation parameters...")
            
            for props in [hypocaust_props, modern_props]:
                props.update({
                    'source_temp': source_temp,
                    'efficiency': efficiency,
                    'fuel_type': fuel_type
                })
            
            # Create simulation instances
            progress_container.progress(20)
            status_container.info("Creating simulation instances...")
            
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
            progress_container.progress(40)
            status_container.info("Updating system parameters...")
            
            hypocaust_sim.update_system_params(hypocaust_params)
            modern_sim.update_system_params(modern_params)
            
            # Calculate temperature distributions
            progress_container.progress(60)
            status_container.info("Calculating temperature distributions...")
            
            hypocaust_temp = hypocaust_sim.calculate_heat_transfer(initial_temp, 100)
            modern_temp = modern_sim.calculate_heat_transfer(initial_temp, 100)
            
            # Create visualizer
            progress_container.progress(80)
            status_container.info("Generating visualizations...")
            visualizer = HeatingVisualizer()

            # Clear progress indicators
            progress_container.empty()
            status_container.success("Simulation completed successfully!")
            
            # 1. System Diagrams
            st.header("System Diagrams")
            st.info("Technical diagrams showing the components and heat flow patterns in both heating systems")
            col1, col2 = st.columns(2)
            with col1:
                st.write("Hypocaust System")
                st.image(visualizer.create_system_diagram('hypocaust'))
            with col2:
                st.write("Modern Heating System")
                st.image(visualizer.create_system_diagram('modern'))
            
            st.divider()
            
            # 2. 2D Heat Maps
            st.header("2D Temperature Distribution")
            st.info("Top-down view of temperature distribution across the room")
            col3, col4 = st.columns(2)
            with col3:
                st.write("Hypocaust System")
                st.pyplot(visualizer.create_heatmap(hypocaust_temp))
            with col4:
                st.write("Modern System")
                st.pyplot(visualizer.create_heatmap(modern_temp))
            
            st.divider()
            
            # 3. Heat Distribution (3D)
            st.header("3D Heat Distribution")
            st.info("Three-dimensional visualization of temperature gradients")
            col5, col6 = st.columns(2)
            with col5:
                st.write("Hypocaust System")
                st.plotly_chart(
                    visualizer.create_3d_heatmap(
                        hypocaust_temp,
                        (room_size['length'], room_size['width'])
                    ),
                    use_container_width=True
                )
            with col6:
                st.write("Modern System")
                st.plotly_chart(
                    visualizer.create_3d_heatmap(
                        modern_temp,
                        (room_size['length'], room_size['width'])
                    ),
                    use_container_width=True
                )
            
            st.divider()
            
            # 4. Energy Retention Analysis
            st.header("Energy Retention Analysis")
            st.info("24-hour comparison of heat retention capabilities")
            hypocaust_hours, hypocaust_retention = hypocaust_sim.calculate_hourly_energy_retention(initial_temp)
            modern_hours, modern_retention = modern_sim.calculate_hourly_energy_retention(initial_temp)
            
            retention_plot = visualizer.create_energy_retention_plot(
                hypocaust_hours, hypocaust_retention, modern_retention
            )
            st.plotly_chart(retention_plot, use_container_width=True)
            
            with st.expander("Energy Retention Details"):
                st.write("""
                The energy retention analysis shows how well each system maintains temperature over time:
                - Hypocaust systems typically show better long-term heat retention due to thermal mass
                - Modern systems offer more responsive temperature control but may cool faster
                - Daily temperature fluctuations affect both systems differently
                """)
            
            st.divider()
            
            # 5. Environmental Impact Analysis
            st.header("Environmental Impact Analysis")
            st.info("Comprehensive comparison of environmental effects")
            
            hypocaust_emissions = hypocaust_sim.calculate_co2_emissions(
                calculate_power_consumption(
                    room_size['length'] * room_size['width'] * room_size['height'],
                    temp_diff,
                    hypocaust_sim.properties['efficiency']
                ),
                24
            )
            modern_emissions = modern_sim.calculate_co2_emissions(
                calculate_power_consumption(
                    room_size['length'] * room_size['width'] * room_size['height'],
                    temp_diff,
                    modern_sim.properties['efficiency']
                ),
                24
            )
            
            tabs = st.tabs([
                "Operational Emissions",
                "Embodied Carbon",
                "Maintenance Impact",
                "Net Impact"
            ])
            
            with tabs[0]:
                st.subheader("Operational CO₂ Emissions")
                col7, col8 = st.columns(2)
                with col7:
                    st.write("Hypocaust System:")
                    for source, value in hypocaust_emissions['operational'].items():
                        st.write(f"- {source.title()}: {value:.2f} kg CO₂e")
                with col8:
                    st.write("Modern System:")
                    for source, value in modern_emissions['operational'].items():
                        st.write(f"- {source.title()}: {value:.2f} kg CO₂e")
                
                operational_data = {
                    'hypocaust': {'operational': sum(hypocaust_emissions['operational'].values())},
                    'modern': {'operational': sum(modern_emissions['operational'].values())}
                }
                st.plotly_chart(
                    create_emissions_chart(
                        operational_data['hypocaust'],
                        operational_data['modern'],
                        'operational'
                    ),
                    use_container_width=True
                )
            
            with tabs[1]:
                st.subheader("Embodied Carbon")
                col9, col10 = st.columns(2)
                with col9:
                    st.write(f"Hypocaust System: {hypocaust_emissions['embodied_carbon']:.2f} kg CO₂e")
                with col10:
                    st.write(f"Modern System: {modern_emissions['embodied_carbon']:.2f} kg CO₂e")
                
                embodied_data = {
                    'hypocaust': {'embodied': hypocaust_emissions['embodied_carbon']},
                    'modern': {'embodied': modern_emissions['embodied_carbon']}
                }
                st.plotly_chart(
                    create_emissions_chart(
                        embodied_data['hypocaust'],
                        embodied_data['modern'],
                        'embodied'
                    ),
                    use_container_width=True
                )
            
            with tabs[2]:
                st.subheader("Maintenance Impact")
                col11, col12 = st.columns(2)
                with col11:
                    st.write(f"Hypocaust System: {hypocaust_emissions['maintenance_impact']:.2f} kg CO₂e/year")
                with col12:
                    st.write(f"Modern System: {modern_emissions['maintenance_impact']:.2f} kg CO₂e/year")
                
                maintenance_data = {
                    'hypocaust': {'maintenance': hypocaust_emissions['maintenance_impact']},
                    'modern': {'maintenance': modern_emissions['maintenance_impact']}
                }
                st.plotly_chart(
                    create_emissions_chart(
                        maintenance_data['hypocaust'],
                        maintenance_data['modern'],
                        'maintenance'
                    ),
                    use_container_width=True
                )
            
            with tabs[3]:
                st.subheader("Net Environmental Impact")
                col13, col14 = st.columns(2)
                with col13:
                    st.write("Hypocaust System:")
                    st.write(f"- Total Emissions: {hypocaust_emissions['net_emissions']:.2f} kg CO₂e")
                    st.write(f"- Carbon Offset: {hypocaust_emissions['carbon_offset']:.2f} kg CO₂e")
                with col14:
                    st.write("Modern System:")
                    st.write(f"- Total Emissions: {modern_emissions['net_emissions']:.2f} kg CO₂e")
                    st.write(f"- Carbon Offset: {modern_emissions['carbon_offset']:.2f} kg CO₂e")
                
                net_data = {
                    'hypocaust': {'net': hypocaust_emissions['net_emissions']},
                    'modern': {'net': modern_emissions['net_emissions']}
                }
                st.plotly_chart(
                    create_emissions_chart(
                        net_data['hypocaust'],
                        net_data['modern'],
                        'net'
                    ),
                    use_container_width=True
                )
            
            st.divider()
            
            # 6. System Performance
            st.header("System Performance")
            st.info("Comparative analysis of heating efficiency and performance metrics")
            
            hypocaust_metrics = hypocaust_sim.calculate_efficiency(hypocaust_temp)
            modern_metrics = modern_sim.calculate_efficiency(modern_temp)
            
            col15, col16 = st.columns(2)
            with col15:
                st.subheader("Hypocaust System Metrics")
                hypocaust_formatted = format_results(hypocaust_metrics)
                for key, value in hypocaust_formatted.items():
                    st.write(f"- {key.title()}: {value}")
            with col16:
                st.subheader("Modern System Metrics")
                modern_formatted = format_results(modern_metrics)
                for key, value in modern_formatted.items():
                    st.write(f"- {key.title()}: {value}")
            
            st.divider()
            
            # 7. System Equivalency Analysis
            st.header("System Equivalency Analysis")
            st.info("Direct comparison of key performance parameters between systems")
            
            heat_output = system_equiv.calculate_heat_output_equivalency(source_temp, initial_temp)
            response_times = system_equiv.calculate_response_times(temp_diff)
            
            col17, col18 = st.columns(2)
            with col17:
                st.subheader("Heat Output")
                st.write(f"Modern System: {heat_output['modern_output']:.2f} W/m²")
                st.write(f"Hypocaust System: {heat_output['hypocaust_output']:.2f} W/m²")
                st.write(f"Output Ratio: {heat_output['output_ratio']:.2%}")
            
            with col18:
                st.subheader("Response Times")
                st.write(f"Modern System: {response_times['modern_response']:.1f} minutes")
                st.write(f"Hypocaust System: {response_times['hypocaust_response']:.1f} minutes")
                st.write(f"Response Ratio: {response_times['response_ratio']:.1f}x slower for Hypocaust")
            
            st.divider()
            
            # 8. Scientific Justification
            st.header("Scientific Justification")
            st.info("Detailed explanation of the scientific principles behind the comparisons")
            
            justification = system_equiv.get_scientific_justification()
            for aspect, explanation in justification.items():
                with st.expander(aspect.replace('_', ' ').title()):
                    st.write(explanation.strip())
                    st.markdown("""
                    *References:*
                    - Archaeological evidence from Roman sites
                    - Modern thermal engineering principles
                    - Historical documentation and research
                    """)

        except Exception as e:
            error_container.error(f"An error occurred during simulation: {str(e)}")
            st.sidebar.error("Please check your input parameters and try again.")
            traceback.print_exc()

if __name__ == "__main__":
    main()
