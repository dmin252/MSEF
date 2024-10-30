import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw

class HeatingVisualizer:
    def __init__(self, width=800, height=400):
        self.width = width
        self.height = height
        
    def create_system_diagram(self, system_type):
        """Create detailed diagram of heating system"""
        img = Image.new('RGB', (self.width, self.height), 'white')
        draw = ImageDraw.Draw(img)
        
        if system_type == 'hypocaust':
            self._draw_hypocaust(draw)
        else:
            self._draw_modern(draw)
            
        return img
    
    def _draw_hypocaust(self, draw):
        """Draw detailed hypocaust system diagram"""
        # Room outline
        draw.rectangle([50, 50, 750, 350], outline='black')
        
        # Underground chamber
        draw.rectangle([50, 300, 750, 350], outline='black', fill='brown')
        
        # Pillars in staggered arrangement for better heat distribution
        pillar_rows = [(100, 250), (200, 270), (300, 250), (400, 270), 
                      (500, 250), (600, 270), (700, 250)]
        for x, y in pillar_rows:
            draw.rectangle([x, y, x+20, 300], fill='gray')
            
        # Heat source with flame effect
        draw.rectangle([50, 350, 150, 380], fill='red')
        draw.polygon([(70, 350), (90, 330), (110, 350)], fill='orange')
        
        # Air flow patterns
        flow_heights = [310, 320, 330]
        for height in flow_heights:
            for x in range(200, 701, 100):
                # Draw curved flow lines
                draw.arc([x-20, height-10, x+20, height+10], 0, 180, fill='red', width=2)
                # Add arrow
                draw.line([x+20, height, x+30, height], fill='red', width=2)
                draw.line([x+30, height, x+25, height-5], fill='red', width=2)
                draw.line([x+30, height, x+25, height+5], fill='red', width=2)
    
    def _draw_modern(self, draw):
        """Draw detailed modern heating system diagram"""
        # Room outline
        draw.rectangle([50, 50, 750, 350], outline='black')
        
        # Radiator with fins
        base_x, base_y = 100, 100
        draw.rectangle([base_x, base_y, base_x+50, base_y+200], fill='red', outline='black')
        # Add radiator fins
        for y in range(base_y+20, base_y+200, 20):
            draw.rectangle([base_x-10, y, base_x+60, y+5], fill='red', outline='black')
        
        # Heat flow patterns with convection currents
        for y in range(120, 281, 40):
            # Rising heat
            draw.line([160, y, 200, y-20], fill='red', width=2)
            # Convection curve
            points = [(200, y-20), (300, y-30), (400, y-20), (500, y)]
            for i in range(len(points)-1):
                draw.line([points[i][0], points[i][1], points[i+1][0], points[i+1][1]], 
                         fill='red', width=2)
            # Add arrow
            draw.line([500, y, 495, y-5], fill='red', width=2)
            draw.line([500, y, 495, y+5], fill='red', width=2)
            
    def create_heatmap(self, temperature_data):
        """Create detailed heatmap visualization of temperature distribution"""
        plt.figure(figsize=(10, 6))
        plt.imshow(temperature_data, cmap='RdYlBu_r', interpolation='bicubic')
        plt.colorbar(label='Temperature (°C)')
        
        # Add contour lines for better visualization of temperature gradients
        plt.contour(temperature_data, colors='black', alpha=0.5, 
                   levels=np.linspace(temperature_data.min(), temperature_data.max(), 10))
        
        # Convert plot to image
        fig = plt.gcf()
        plt.close()
        
        return fig
