import shutil
from pathlib import Path
import geopandas as gpd
import pandas as pd

from tree_registration_and_matching.utils import ensure_height_is_present

DATA_FOLDER = "/ofo-share/repos/david/shift-eval/data"
OUTPUT_FOLDER = "/ofo-share/repos/david/shift-eval/formatted-data/"
TREES_FILE = "/ofo-share/project-data/species-prediction-project/raw/ground-reference/ofo_ground-reference_trees.gpkg"

APPLY_SHIFT = False

SAVE_TREES = True
SAVE_CHM = False
SAVE_ORTHO = False

trees = gpd.read_file(TREES_FILE)

shift_files = list(Path(DATA_FOLDER).rglob("*ground-reference-shift.csv"))

for shift_file in shift_files:
    shift = pd.read_csv(shift_file)

    # TODO update this
    mission = shift_file.parts[-4]
    plot_id = shift_file.parts[-1].split("_")[1]

    output_file = Path(OUTPUT_FOLDER, mission, f"0_{mission}_{plot_id}.gpkg")

    plot_id = shift_file.name.split("_")[1]

    plot_trees = trees.query("plot_id==@plot_id")

    crs = shift["shift_CRS"].iloc[0]

    plot_trees.to_crs(crs, inplace=True)

    if APPLY_SHIFT:
        plot_trees.geometry = plot_trees.geometry.translate(
            xoff=shift["estimated_shift_x"].iloc[0],
            yoff=shift["estimated_shift_y"].iloc[0],
        )

    # Make sure height is present for visualization
    plot_trees = ensure_height_is_present(plot_trees)

    if len(plot_trees) < 10:
        continue

    output_file.parent.mkdir(exist_ok=True, parents=True)

    if SAVE_TREES:
        plot_trees.to_file(output_file)

    if SAVE_CHM:
        input_CHM_file = Path(
            DATA_FOLDER, mission, "photogrammetry_03", "full", f"{mission}_chm-mesh.tif"
        )
        output_CHM_file = Path(OUTPUT_FOLDER, mission, f"{mission}_chm.tif")

        shutil.copyfile(input_CHM_file, output_CHM_file)

    if SAVE_ORTHO:
        input_ortho_file = Path(
            DATA_FOLDER,
            mission,
            "photogrammetry_03",
            "full",
            f"{mission}_ortho-dsm-ptcloud.tif",
        )
        output_ortho_file = Path(OUTPUT_FOLDER, mission, f"{mission}_ortho.tif")

        shutil.copyfile(input_ortho_file, output_ortho_file)
