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
SHIFT_FILE = Path("/ofo-share/repos/david/shift-eval/data/computed_shifts.csv")
PLOT_BOUNDS_FILE = Path(
    "/ofo-share/project-data/species-prediction-project/raw/ground-reference/ofo_ground-reference_plots.gpkg"
)

df = pd.read_csv(ASSESSMENT_FILE)


f, axs = plt.subplots(1, 2)
f.set_figheight(6)
f.set_figwidth(10)

all_shifts = pd.read_csv(SHIFT_FILE)
all_plot_bounds = gpd.read_file(PLOT_BOUNDS_FILE)

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

    print(f"showing tree file {tree_file}")

    trees = gpd.read_file(tree_file)

    plot_id_str = f"{plot_id:04}"
    bounds = all_plot_bounds.query("plot_id==@plot_id_str").copy()
    shift_row = all_shifts.query(
        "plot_id==@plot_id & mission_id==@drone_mission_id"
    ).copy()
    assert len(bounds) == 1
    assert len(shift_row) == 1

    working_crs = int(shift_row.iloc[0]["working_crs"])
    x_shift = float(shift_row.iloc[0]["shift_x"])
    y_shift = float(shift_row.iloc[0]["shift_y"])

    bounds.to_crs(working_crs, inplace=True)
    bounds.geometry = bounds.translate(xoff=x_shift, yoff=y_shift)

    plot_trees_on_raster(
        CHM_file, trees, plot_bounds=bounds, ax=axs[0], add_colorbar=False
    )
    plot_trees_on_raster(ortho_file, trees, plot_bounds=bounds, ax=axs[1])

    output_path = Path(
        OUTPUT_FOLDER, quality, f"{drone_mission_id:06}_{plot_id:04}.png"
    )

    output_path.parent.mkdir(exist_ok=True, parents=True)

    plt.savefig(output_path)

    # Clear the axes
    axs[0].clear()
    axs[1].clear()
