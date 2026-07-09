from pathlib import Path
import geopandas as gpd
import numpy as np
import pandas as pd

from tree_registration_and_matching.utils import (
    ensure_projected_CRS,
    ensure_height_is_present,
    is_overstory,
)

UNSHIFTED_TREES_FILE = Path(
    "/ofo-share/project-data/species-prediction-project/raw/ground-reference/ofo_ground-reference_trees.gpkg"
)
SHIFTED_FILES = Path("/ofo-share/scratch/xiaoya/tree_registration_annotation/data/")
OUTPUT_FILE = Path("/ofo-share/repos/david/shift-eval/data/computed_shifts.csv")

shifted_files = SHIFTED_FILES.rglob("a_*")

unshifted_trees = gpd.read_file(UNSHIFTED_TREES_FILE)

manual_shifts = []

for i, f in enumerate(shifted_files):
    shifted_plot_trees = gpd.read_file(f)
    _, mission_id, plot_id = f.name.split(".")[0].split("_")

    unshifted_plot_trees = unshifted_trees.query("plot_id == @plot_id")

    # Make sure height is present for visualization
    unshifted_plot_trees = ensure_height_is_present(unshifted_plot_trees)

    # Remove trees which are explicitly marked as dead
    live_trees = unshifted_plot_trees.live_dead != "D"
    unshifted_plot_trees = unshifted_plot_trees[live_trees]

    # Ensure only overstory trees are present
    overstory_trees = is_overstory(unshifted_plot_trees)
    unshifted_plot_trees = unshifted_plot_trees[overstory_trees]

    if len(unshifted_plot_trees) != len(shifted_plot_trees):
        breakpoint()
        raise ValueError()

    shifted_plot_trees = ensure_projected_CRS(shifted_plot_trees)

    working_crs = shifted_plot_trees.crs

    unshifted_plot_trees.to_crs(working_crs, inplace=True)

    shifted_coords = shifted_plot_trees.geometry.get_coordinates().to_numpy()
    unshifted_coords = unshifted_plot_trees.geometry.get_coordinates().to_numpy()
    shift = np.mean(shifted_coords - unshifted_coords, axis=0)

    manual_shifts.append(
        {
            "mission_id": mission_id,
            "plot_id": plot_id,
            "working_crs": working_crs.to_epsg(),
            "shift_x": float(shift[0]),
            "shift_y": float(shift[1]),
        }
    )

manual_shifts_df = pd.DataFrame(manual_shifts)

manual_shifts_df.to_csv(OUTPUT_FILE)
