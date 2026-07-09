from tree_registration_and_matching.utils import ensure_projected_CRS
from tree_registration_and_matching.vis import plot_trees_on_raster
import matplotlib.pyplot as plt
import rasterio as rio

import geopandas as gpd
import pandas as pd

from pathlib import Path

ASSESSMENT_FILE = "/ofo-share/scratch/david/show-registered-data/Tree registration assessment Xiaoya - gpkg_files.csv"
INPUT_FOLDER = "/ofo-share/scratch/xiaoya/tree_registration_annotation/data"
OUTPUT_FOLDER = "/ofo-share/scratch/david/show-registered-data/outputs"

df = pd.read_csv(ASSESSMENT_FILE)


f, axs = plt.subplots(1, 2)
f.set_figheight(6)
f.set_figwidth(10)

for _, row in df.iterrows():
    drone_mission_id = int(row["Drone mission ID"])
    plot_id = int(row["Plot ID"])
    quality = row["Quality of alignment after registration"]

    tree_file = Path(
        INPUT_FOLDER,
        f"{drone_mission_id:06}",
        f"a_{drone_mission_id:06}_{plot_id:04}.gpkg",
    )
    CHM_file = Path(
        INPUT_FOLDER, f"{drone_mission_id:06}", f"b_{drone_mission_id:06}_chm.tif"
    )
    ortho_file = Path(
        INPUT_FOLDER, f"{drone_mission_id:06}", f"c_{drone_mission_id:06}_ortho.tif"
    )

    trees = ensure_projected_CRS(gpd.read_file(tree_file))
    bounds = gpd.GeoDataFrame(geometry=[trees.buffer(30).union_all()], crs=trees.crs)

    plot_trees_on_raster(
        CHM_file, trees, plot_bounds=bounds, ax=axs[0], add_colorbar=False
    )
    plot_trees_on_raster(ortho_file, trees, plot_bounds=bounds, ax=axs[1])

    output_path = Path(
        OUTPUT_FOLDER, quality, f"{drone_mission_id:06}_{plot_id:04}.png"
    )

    output_path.parent.mkdir(exist_ok=True)

    plt.savefig(output_path)

    # Clear the axes
    axs[0].clear()
    axs[1].clear()
