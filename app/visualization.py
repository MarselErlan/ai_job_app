"""
Visualization module for project analysis using matplotlib
"""

import matplotlib.pyplot as plt
import numpy as np

def create_codebase_distribution_chart():
    # Create figure and axis with specific size and aspect ratio
    fig, ax = plt.subplots(figsize=(10, 6), subplot_kw=dict(aspect="equal"))

    # Data from the project analysis
    categories = [
        "Core Pipeline",
        "Service Layer",
        "API & Web Layer",
        "Database Layer",
        "Other",
        "Infrastructure",
        "Configuration"
    ]

    # Lines of code for each category
    lines_of_code = [930, 815, 523, 431, 409, 351, 34]

    # Calculate percentages for better visualization
    percentages = [f"{(loc/sum(lines_of_code))*100:.1f}%" for loc in lines_of_code]

    # Create the donut chart
    wedges, texts = ax.pie(lines_of_code, 
                          wedgeprops=dict(width=0.5),  # This creates the donut shape
                          startangle=-40)  # Rotate to make it look better

    # Properties for the annotation boxes
    bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
    kw = dict(arrowprops=dict(arrowstyle="-"),
              bbox=bbox_props, zorder=0, va="center")

    # Add annotations with lines pointing to each section
    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1)/2. + p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        connectionstyle = f"angle,angleA=0,angleB={ang}"
        kw["arrowprops"].update({"connectionstyle": connectionstyle})
        
        # Create label with both category and percentage
        label = f"{categories[i]}\n{percentages[i]}"
        
        ax.annotate(label, 
                   xy=(x, y), 
                   xytext=(1.35*np.sign(x), 1.4*y),
                   horizontalalignment=horizontalalignment, 
                   **kw)

    # Add title
    ax.set_title("AI Job Application System\nCodebase Distribution", pad=20)

    return fig

if __name__ == "__main__":
    # Create and show the chart
    fig = create_codebase_distribution_chart()
    plt.show() 