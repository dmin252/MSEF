import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw

class HeatingVisualizer:
    def __init__(self, width=800, height=400):
        self.width = width
        self.height = height
        
    def create_system_diagram(self, system_type):
        """Create basic diagram of heating system"""
        img = Image.new('RGB', (self.width, self.height), 'white')
        draw = ImageDraw.Draw(img)
        
        if system_type == 'hypocaust':
            self._draw_hypocaust(draw)
        else:
            self._draw_modern(draw)
            
        return img
    
    def _draw_hypocaust(self, draw):
        """Draw hypocaust system diagram"""
        # Floor
        draw.rectangle([50, 300, 750, 350], outline='black', fill='brown')
        
        # Pillars
        pillar_positions = range(100, 701, 100)
        for x in pillar_positions:
            draw.rectangle([x, 250, x+20, 300], fill='gray')
            
        # Heat source
        draw.rectangle([50, 350, 150, 380], fill='red')
        
        # Air flow indicators
        for x in range(200, 701, 100):
            draw.line([x, 320, x+30, 320], fill='red', width=2)
            draw.line([x+30, 320, x+20, 315], fill='red', width=2)
            draw.line([x+30, 320, x+20, 325], fill='red', width=2)
    
    def _draw_modern(self, draw):
        """Draw modern heating system diagram"""
        # Room outline
        draw.rectangle([50, 50, 750, 350], outline='black')
        
        # Radiator
        draw.rectangle([100, 100, 150, 300], fill='red', outline='black')
        
        # Heat flow indicators
        for y in range(120, 281, 40):
            draw.line([160, y, 200, y-10], fill='red', width=2)
            draw.arc([200, y-20, 220, y], 0, 359, fill='red')
            
    def create_heatmap(self, temperature_data):
        """Create heatmap visualization of temperature distribution"""
        plt.figure(figsize=(10, 6))
        plt.imshow(temperature_data, cmap='hot', interpolation='nearest')
        plt.colorbar(label='Temperature (°C)')
        
        # Convert plot to image
        fig = plt.gcf()
        plt.close()
        
        return fig
