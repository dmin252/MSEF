"""Material properties database for thermal simulation"""

class MaterialDatabase:
    def __init__(self):
        # Common building materials
        self.building_materials = {
            # Ancient Roman Materials
            'roman_concrete': {
                'name': 'Roman Concrete (Opus Caementicium)',
                'thermal_conductivity': 0.29,
                'specific_heat': 880,
                'density': 1900,
                'thermal_mass': 1672000,  # J/m³K
                'emissivity': 0.85,
                'thermal_resistance': 0.172,  # m²K/W per 0.05m thickness
                'description': 'Ancient Roman concrete made with volcanic ash and lime',
                'period': 'ancient'
            },
            'roman_brick': {
                'name': 'Roman Brick (Laterus)',
                'thermal_conductivity': 0.72,
                'specific_heat': 840,
                'density': 1800,
                'thermal_mass': 1512000,
                'emissivity': 0.93,
                'thermal_resistance': 0.069,
                'description': 'Traditional Roman bricks used in construction',
                'period': 'ancient'
            },
            'tuff_stone': {
                'name': 'Volcanic Tuff Stone',
                'thermal_conductivity': 0.55,
                'specific_heat': 1100,
                'density': 1500,
                'thermal_mass': 1650000,
                'emissivity': 0.89,
                'thermal_resistance': 0.091,
                'description': 'Volcanic rock commonly used in Roman construction',
                'period': 'ancient'
            },
            'marble': {
                'name': 'Roman Marble',
                'thermal_conductivity': 2.8,
                'specific_heat': 880,
                'density': 2700,
                'thermal_mass': 2376000,
                'emissivity': 0.95,
                'thermal_resistance': 0.018,
                'description': 'Decorative and functional stone material',
                'period': 'ancient'
            },
            'opus_testaceum': {
                'name': 'Opus Testaceum',
                'thermal_conductivity': 0.64,
                'specific_heat': 850,
                'density': 1700,
                'thermal_mass': 1445000,
                'emissivity': 0.91,
                'thermal_resistance': 0.078,
                'description': 'Roman brick-faced concrete',
                'period': 'ancient'
            },
            'opus_latericium': {
                'name': 'Opus Latericium',
                'thermal_conductivity': 0.58,
                'specific_heat': 840,
                'density': 1600,
                'thermal_mass': 1344000,
                'emissivity': 0.90,
                'thermal_resistance': 0.086,
                'description': 'Roman brick-work construction',
                'period': 'ancient'
            },
            
            # Modern Materials
            'concrete': {
                'name': 'Modern Concrete',
                'thermal_conductivity': 1.7,
                'specific_heat': 920,
                'density': 2300,
                'thermal_mass': 2116000,
                'emissivity': 0.94,
                'thermal_resistance': 0.029,
                'description': 'Standard modern concrete mix',
                'period': 'modern'
            },
            'brick': {
                'name': 'Modern Brick',
                'thermal_conductivity': 0.84,
                'specific_heat': 800,
                'density': 1700,
                'thermal_mass': 1360000,
                'emissivity': 0.93,
                'thermal_resistance': 0.060,
                'description': 'Standard clay brick',
                'period': 'modern'
            },
            'mineral_wool': {
                'name': 'Mineral Wool Insulation',
                'thermal_conductivity': 0.04,
                'specific_heat': 840,
                'density': 30,
                'thermal_mass': 25200,
                'emissivity': 0.95,
                'thermal_resistance': 1.250,
                'description': 'Modern thermal insulation material',
                'period': 'modern'
            },
            'polyurethane_foam': {
                'name': 'Polyurethane Foam Insulation',
                'thermal_conductivity': 0.025,
                'specific_heat': 1400,
                'density': 35,
                'thermal_mass': 49000,
                'emissivity': 0.90,
                'thermal_resistance': 2.000,
                'description': 'High-performance modern insulation',
                'period': 'modern'
            },
        }
        
        # Heating system specific materials
        self.heating_materials = {
            # Hypocaust System Materials
            'terracotta_pipe': {
                'name': 'Terracotta Pipes (Tubuli)',
                'thermal_conductivity': 0.93,
                'specific_heat': 920,
                'density': 1800,
                'heat_transfer_coefficient': 25,
                'emissivity': 0.93,
                'thermal_resistance': 0.054,
                'air_flow_resistance': 0.15,  # Pa·s/m³
                'description': 'Vertical heating pipes in Roman hypocaust',
                'period': 'ancient'
            },
            'hypocaust_pillar': {
                'name': 'Hypocaust Pillar (Pilae)',
                'thermal_conductivity': 0.72,
                'specific_heat': 840,
                'density': 1800,
                'heat_transfer_coefficient': 20,
                'emissivity': 0.91,
                'thermal_resistance': 0.069,
                'load_bearing_capacity': 50,  # kN
                'description': 'Support pillars in hypocaust system',
                'period': 'ancient'
            },
            'suspensura_tiles': {
                'name': 'Suspensura Floor Tiles',
                'thermal_conductivity': 0.84,
                'specific_heat': 860,
                'density': 1850,
                'heat_transfer_coefficient': 22,
                'emissivity': 0.92,
                'thermal_resistance': 0.060,
                'thickness_range': [0.04, 0.08],  # m
                'description': 'Raised floor tiles in hypocaust',
                'period': 'ancient'
            },
            
            # Modern Heating Materials
            'copper_pipe': {
                'name': 'Copper Pipe',
                'thermal_conductivity': 401,
                'specific_heat': 385,
                'density': 8960,
                'heat_transfer_coefficient': 55,
                'emissivity': 0.87,
                'thermal_resistance': 0.00012,
                'pressure_rating': 1600,  # kPa
                'description': 'Modern heating system pipes',
                'period': 'modern'
            },
            'steel_radiator': {
                'name': 'Steel Radiator',
                'thermal_conductivity': 50,
                'specific_heat': 460,
                'density': 7850,
                'heat_transfer_coefficient': 45,
                'emissivity': 0.90,
                'thermal_resistance': 0.001,
                'max_operating_pressure': 1000,  # kPa
                'description': 'Modern heating radiator',
                'period': 'modern'
            },
            'aluminum_radiator': {
                'name': 'Aluminum Radiator',
                'thermal_conductivity': 237,
                'specific_heat': 900,
                'density': 2700,
                'heat_transfer_coefficient': 50,
                'emissivity': 0.88,
                'thermal_resistance': 0.00021,
                'max_operating_pressure': 800,  # kPa
                'description': 'Modern aluminum heating radiator',
                'period': 'modern'
            },
        }

    def get_building_material(self, material_name):
        """Get properties of a building material"""
        return self.building_materials.get(material_name)

    def get_heating_material(self, material_name):
        """Get properties of a heating system material"""
        return self.heating_materials.get(material_name)

    def get_materials_by_period(self, period):
        """Get all materials from a specific period (ancient/modern)"""
        building = {k: v for k, v in self.building_materials.items() 
                   if v['period'] == period}
        heating = {k: v for k, v in self.heating_materials.items() 
                   if v['period'] == period}
        return {'building': building, 'heating': heating}

    def calculate_thermal_diffusivity(self, material):
        """Calculate thermal diffusivity from basic properties"""
        return material['thermal_conductivity'] / (material['density'] * material['specific_heat'])

    def calculate_heat_capacity(self, material, volume):
        """Calculate heat capacity for a given volume of material"""
        return material['density'] * material['specific_heat'] * volume

    def get_material_comparison(self, material1_name, material2_name):
        """Compare properties of two materials"""
        mat1 = self.get_building_material(material1_name) or self.get_heating_material(material1_name)
        mat2 = self.get_building_material(material2_name) or self.get_heating_material(material2_name)
        
        if not (mat1 and mat2):
            return None
            
        return {
            'thermal_conductivity_ratio': mat1['thermal_conductivity'] / mat2['thermal_conductivity'],
            'thermal_mass_ratio': (mat1['density'] * mat1['specific_heat']) / 
                                (mat2['density'] * mat2['specific_heat']),
            'density_ratio': mat1['density'] / mat2['density'],
            'thermal_resistance_ratio': mat1.get('thermal_resistance', 0) / 
                                     mat2.get('thermal_resistance', 1),
            'emissivity_ratio': mat1.get('emissivity', 0) / mat2.get('emissivity', 1)
        }

    def get_recommended_materials(self, application, period=None):
        """Get recommended materials for specific application"""
        if application == 'insulation':
            materials = {k: v for k, v in self.building_materials.items() 
                       if v['thermal_conductivity'] < 0.1}
        elif application == 'heat_transfer':
            materials = {k: v for k, v in self.heating_materials.items() 
                       if v.get('heat_transfer_coefficient', 0) > 30}
        elif application == 'structural':
            materials = {k: v for k, v in self.building_materials.items() 
                       if v['density'] > 1500}
        else:
            return {}

        if period:
            materials = {k: v for k, v in materials.items() if v['period'] == period}
        
        return materials
