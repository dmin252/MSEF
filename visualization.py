import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

class HeatingVisualizer:
    def __init__(self, width=800, height=400):
        self.width = width
        self.height = height
        self.font_size = 12
        try:
            self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", self.font_size)
        except:
            self.font = ImageFont.load_default()

    # [Previous methods remain unchanged...]
    
    def create_time_series_plot(self, hypocaust_data, modern_data):
        """Create interactive time series comparison plot"""
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=('Mean Temperature Over Time', 
                          'Temperature Uniformity Over Time',
                          'System Efficiency Over Time'),
            vertical_spacing=0.12
        )
        
        # Extract data
        time_steps_h = [d['time_step'] for d in hypocaust_data]
        time_steps_m = [d['time_step'] for d in modern_data]
        
        metrics = ['mean_temperature', 'uniformity', 'efficiency']
        labels = ['Temperature (°C)', 'Uniformity', 'Efficiency']
        row = 1
        
        for metric, label in zip(metrics, labels):
            # Hypocaust system data
            fig.add_trace(
                go.Scatter(
                    x=time_steps_h,
                    y=[d[metric] for d in hypocaust_data],
                    name=f'Hypocaust {metric.replace("_", " ").title()}',
                    line=dict(color='firebrick')
                ),
                row=row, col=1
            )
            
            # Modern system data
            fig.add_trace(
                go.Scatter(
                    x=time_steps_m,
                    y=[d[metric] for d in modern_data],
                    name=f'Modern {metric.replace("_", " ").title()}',
                    line=dict(color='royalblue')
                ),
                row=row, col=1
            )
            
            # Update y-axis labels
            fig.update_yaxes(title_text=label, row=row, col=1)
            row += 1
        
        # Update layout
        fig.update_layout(
            height=800,
            showlegend=True,
            title_text="Time Series Analysis of Heating Systems",
            xaxis3_title="Time Steps",
            hovermode='x unified'
        )
        
        return fig
    
    def create_efficiency_radar_plot(self, hypocaust_latest, modern_latest):
        """Create radar plot comparing latest efficiency metrics"""
        categories = ['Mean Temperature', 'Uniformity', 'Efficiency']
        
        fig = go.Figure()
        
        # Normalize values for radar plot
        max_values = {
            'mean_temperature': max(hypocaust_latest['mean_temperature'], 
                                  modern_latest['mean_temperature']),
            'uniformity': 1.0,
            'efficiency': 1.0
        }
        
        # Add hypocaust data
        fig.add_trace(go.Scatterpolar(
            r=[hypocaust_latest['mean_temperature'] / max_values['mean_temperature'],
               hypocaust_latest['uniformity'],
               hypocaust_latest['efficiency']],
            theta=categories,
            fill='toself',
            name='Hypocaust System',
            line_color='firebrick'
        ))
        
        # Add modern system data
        fig.add_trace(go.Scatterpolar(
            r=[modern_latest['mean_temperature'] / max_values['mean_temperature'],
               modern_latest['uniformity'],
               modern_latest['efficiency']],
            theta=categories,
            fill='toself',
            name='Modern System',
            line_color='royalblue'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )),
            showlegend=True,
            title="System Performance Comparison"
        )
        
        return fig

    # [Rest of the previous methods remain unchanged...]
