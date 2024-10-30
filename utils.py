def validate_input(value, min_val, max_val, default):
    """Validate numeric input within range"""
    try:
        val = float(value)
        if min_val <= val <= max_val:
            return val
        return default
    except ValueError:
        return default

def calculate_power_consumption(volume, temp_diff, efficiency):
    """Calculate power consumption in kWh"""
    # Specific heat capacity of air (kJ/kg°C)
    c_air = 1.005
    # Air density (kg/m³)
    rho_air = 1.225
    
    # Energy required = mass * specific heat * temperature difference
    energy = volume * rho_air * c_air * temp_diff
    
    # Convert to kWh and account for efficiency
    return (energy / 3600) / efficiency

def format_results(metrics):
    """Format simulation results for display"""
    return {
        'efficiency': f"{metrics['efficiency']*100:.1f}%",
        'mean_temp': f"{metrics['mean_temperature']:.1f}°C",
        'uniformity': f"{metrics['uniformity']*100:.1f}%"
    }
