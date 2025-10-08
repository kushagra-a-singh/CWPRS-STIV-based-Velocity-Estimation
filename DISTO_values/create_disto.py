# create_fake_disto_dxf.py
import ezdxf

doc = ezdxf.new('R2010')
msp = doc.modelspace()

# Add a few sample points (simulating DISTO measurements)
points = [(0,0,0), (2,0,0), (2,2,1), (0,2,1)]
for p in points:
    msp.add_point(p)

doc.saveas("sample_3D.dxf")
print("Saved sample_3D.dxf")
