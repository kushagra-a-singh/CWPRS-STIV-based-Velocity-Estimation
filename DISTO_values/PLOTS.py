import json
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# Load the calibrated data
with open('discharge_freehelper.json') as f:
    data = json.load(f)

# Extract coordinates
markers = np.array([data['markers_world_coordinates']['x'],
                    data['markers_world_coordinates']['y'],
                    data['markers_world_coordinates']['z']])
shoreline = np.array([data['shoreline']['x'],
                      data['shoreline']['y'],
                      data['shoreline']['z']])
profile = np.array([data['profile']['x'],
                    data['profile']['y'],
                    data['profile']['z']])

# Create a 3D plot
fig = plt.figure(figsize=(10,6))
ax = fig.add_subplot(111, projection='3d')

# Plot markers (GCPs)
ax.scatter(markers[0], markers[1], markers[2], color='red', s=50, label='Markers')

# Plot shoreline
ax.plot(shoreline[0], shoreline[1], shoreline[2], color='green', marker='*', label='Shoreline')

# Plot cross-section as a line
ax.plot(profile[0], profile[1], profile[2], color='blue', label='Cross-section')

# Optionally, add a filled surface for cross-section
verts = [list(zip(profile[0], profile[1], profile[2]))]
poly = Poly3DCollection(verts, alpha=0.3, facecolor='blue')
ax.add_collection3d(poly)

# Labels and legend
ax.set_xlabel('X [m]')
ax.set_ylabel('Y [m]')
ax.set_zlabel('Z [m]')
ax.set_title('3D River Cross-Section and Shoreline')
ax.legend()
plt.savefig("river_cross_section.png", dpi=300)
print("Plot saved as river_cross_section.png")