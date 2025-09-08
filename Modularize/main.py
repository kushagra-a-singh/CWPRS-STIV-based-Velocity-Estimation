from common.lib.CamConfig import CamConfig 
from common.lib.Processing import * 

Video_path = "Modularize/ngwerere_20191103.mp4"
outPath = "Modularize/test.json"

gcps = dict(
    src=[
        [1421, 1001],   # Values to be switched with variables that will get the values from the website 
        [1251, 460],
        [421, 432],
        [470, 607]
    ],
    dst = [
    [642735.8076, 8304292.1190],  # lowest right coordinate
    [642737.5823, 8304295.593],  # highest right coordinate
    [642732.7864, 8304298.4250],  # highest left coordinate
    [642732.6705, 8304296.8580]  # highest right coordinate
    ],
    z_0 = 1182.2 
)

corners = [
    [292, 817],
    [50, 166],
    [1200, 236],    # x,Y coordinates (column,row)
    [1600, 834]     
]

cfg = CamConfig(Video_path , gcps , corners , outPath)

bbox_coords = [   # Approx. border of water , User ip from the website 
    [150, 0],
    [500, 1079],
    [1750, 1079],
    [900, 0]
]

NCPath = "Modularize/test.nc"
piv = process(Video_path , outPath , bbox_coords , NCPath)


maskPath = "Modularize/test_mask.nc"
mask_piv = mask(Video_path , NCPath , maskPath)


