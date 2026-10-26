#!/usr/bin/env python3

from __future__ import annotations

import argparse
import shutil
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedSeq


# =============================================================================
# PATHS
# =============================================================================

SOURCE_DIR = Path(
    "/home/s0shar47/scratch/salil/DPL/dPL_Hydro_SNTEMP"
)

DPL_ROOT = Path(
    "/home/s0shar47/scratch/salil/DPL/CASES"
)

CONFIG_RELATIVE = Path(
    "config/config_hydro_temp.yaml"
)


# =============================================================================
# TEMPORAL SETTINGS (Dr. Feng's Pure LSTM 2020 setup)
# =============================================================================

TEMPORAL_CONFIG = {
    "tRange": [19800101, 20141231],
    "t_train": [19801001, 19950930],
    "t_test": [19951001, 20100930],
}


# =============================================================================
# EXPERIMENT DEFINITIONS
# =============================================================================

HYDRO_MODELS = [
    "HBV",
    "HBV_capillary",
    "marrmot_PRMS",
]


HYDRO_DYNAMIC_PARAMS = {
    "HBV": [
        "parBETA",
        "parBETAET",
    ],

    "HBV_capillary": [
        "parBETA",
        "parK0",
        "parUZL",
        "parBETAET",
    ],

    "marrmot_PRMS": [
        "scx",
        "cgw",
        "alpha",
        "tt",
    ],
}


# -------------------------------------------------------------------------
# Baseflow separation methods and corresponding forcing files
# -------------------------------------------------------------------------

METHOD_FORCING_PATHS = {

    "Furey": (
        "/scratch/data/CAMELS_FORCING/"
        "daymet_19800101_20141231_forcing_671_baseflow_mmday.npy"
    ),

    "Eckhardt": (
        "/scratch/data/CAMELS_FORCING/"
        "daymet_19800101_20141231_forcing_671_eckhardt_mmday.npy"
    ),

    "LocalHYSEP": (
        "/scratch/data/CAMELS_FORCING/"
        "daymet_19800101_20141231_forcing_671_LocalHYSEP_mmday.npy"
    ),

    "USGS": (
        "/scratch/data/CAMELS_FORCING/"
        "daymet_19800101_20141231_forcing_671_usgs.npy"
    ),
}


# -------------------------------------------------------------------------
# Loss functions
# -------------------------------------------------------------------------

LOSS_FUNCTIONS = [
    "RmseLoss_flow_baseflow",
    "RmseLoss1_flow_baseflow",
    "NseLoss_flow_baseflow",
]


# -------------------------------------------------------------------------
# Weight combinations
#
# 5050 = w1=0.50, w2=0.50
# 7525 = w1=0.75, w2=0.25
# 2575 = w1=0.25, w2=0.75
# -------------------------------------------------------------------------

WEIGHT_COMBINATIONS = [
    (0.50, 0.50, "5050"),
    (0.75, 0.25, "7525"),
    (0.25, 0.75, "2575"),
]


# =============================================================================
# YAML FUNCTIONS
# =============================================================================

def load_yaml(path: Path) -> Any:
    """Load YAML while preserving formatting/comments where possible."""

    yaml = YAML()
    yaml.preserve_quotes = True

    with path.open("r") as f:
        return yaml.load(f)


def save_yaml(cfg: Any, path: Path) -> None:
    """Save YAML."""

    yaml = YAML()
    yaml.preserve_quotes = True

    with path.open("w") as f:
        yaml.dump(cfg, f)


def set_flow_list(
    cfg: Any,
    key: str,
    values: list[Any],
) -> None:
    """
    Write a YAML list in flow style.

    Example:

        Action: [0, 1]

    instead of:

        Action:
          - 0
          - 1
    """

    seq = CommentedSeq(values)
    seq.fa.set_flow_style()

    cfg[key] = seq

    if hasattr(cfg, "ca") and key in cfg.ca.items:
        del cfg.ca.items[key]


# =============================================================================
# CONFIGURATION
# =============================================================================

def configure_case(
    config_path: Path,
    hydro: str,
    method: str,
    loss_function: str,
    w1: float,
    w2: float,
    weight_tag: str,
) -> None:
    """
    Modify the copied config for one experiment.

    Only the copied config is changed.
    The original source config is never modified.
    """

    cfg = load_yaml(config_path)

    # -------------------------------------------------------------------------
    # Hydro model
    # -------------------------------------------------------------------------

    cfg["hydro_model_name"] = hydro

    set_flow_list(
        cfg,
        "dyn_params_list_hydro",
        HYDRO_DYNAMIC_PARAMS[hydro],
    )

    # -------------------------------------------------------------------------
    # Baseflow method / forcing
    # -------------------------------------------------------------------------

    cfg["forcing_path"] = METHOD_FORCING_PATHS[method]

    # -------------------------------------------------------------------------
    # Loss function
    # -------------------------------------------------------------------------

    cfg["loss_function"] = loss_function

    # -------------------------------------------------------------------------
    # Loss weights
    # -------------------------------------------------------------------------

    if "loss_function_weights" not in cfg:
        raise RuntimeError(
            f"'loss_function_weights' was not found in:\n"
            f"{config_path}"
        )

    cfg["loss_function_weights"]["w1"] = float(w1)
    cfg["loss_function_weights"]["w2"] = float(w2)

    # -------------------------------------------------------------------------
    # Output Model Path (Dynamic per case)
    # -------------------------------------------------------------------------

    output_model_path = f"/home/s0shar47/scratch/salil/DPL/CASES/{method}/{hydro}/{loss_function}/{weight_tag}/OUTPUTS/"
    cfg["output_model"] = output_model_path

    # -------------------------------------------------------------------------
    # Temporal Test Settings (Dr. Feng's Pure LSTM 2020)
    # -------------------------------------------------------------------------

    for time_key, time_vals in TEMPORAL_CONFIG.items():
        set_flow_list(cfg, time_key, time_vals)

    # -------------------------------------------------------------------------
    # Train + test Action
    #
    # Action:
    #   0 = Train
    #   1 = Test
    # -------------------------------------------------------------------------

    set_flow_list(
        cfg,
        "Action",
        [0, 1],
    )

    # -------------------------------------------------------------------------
    # Save modified config
    # -------------------------------------------------------------------------

    save_yaml(
        cfg,
        config_path,
    )


# =============================================================================
# DIRECTORY NAME
# =============================================================================

def case_relative_path(
    method: str,
    hydro: str,
    loss_function: str,
    weight_tag: str,
) -> Path:
    """
    Build:

        method/hydro/loss/weight
    """

    return (
        Path(method)
        / hydro
        / loss_function
        / weight_tag
    )


# =============================================================================
# CREATE ONE CASE
# =============================================================================

def create_case(
    method: str,
    hydro: str,
    loss_function: str,
    w1: float,
    w2: float,
    weight_tag: str,
    overwrite: bool,
) -> Path:

    relative_path = case_relative_path(
        method=method,
        hydro=hydro,
        loss_function=loss_function,
        weight_tag=weight_tag,
    )

    destination = DPL_ROOT / relative_path
    output_model_path = f"/home/s0shar47/scratch/salil/DPL/CASES/{method}/{hydro}/{loss_function}/{weight_tag}/OUTPUTS/"

    print()
    print("-" * 80)

    print(
        f"Creating case:"
    )

    print(
        f"    {destination}"
    )

    print()

    print(
        f"    Method      : {method}"
    )

    print(
        f"    Hydro model  : {hydro}"
    )

    print(
        f"    Loss         : {loss_function}"
    )

    print(
        f"    w1           : {w1}"
    )

    print(
        f"    w2           : {w2}"
    )

    print(
        f"    output_model : {output_model_path}"
    )

    print(
        f"    tRange       : {TEMPORAL_CONFIG['tRange']}"
    )

    print(
        f"    t_train      : {TEMPORAL_CONFIG['t_train']}"
    )

    print(
        f"    t_test       : {TEMPORAL_CONFIG['t_test']}"
    )

    print(
        f"    Action       : [0, 1]"
    )

    print(
        f"    Forcing file : {METHOD_FORCING_PATHS[method]}"
    )

    # -------------------------------------------------------------------------
    # Existing case
    # -------------------------------------------------------------------------

    if destination.exists():

        if not overwrite:

            print(
                "    SKIP: directory already exists."
            )

            print(
                "        Use --overwrite to recreate it."
            )

            return destination

        print(
            "    Removing existing directory..."
        )

        shutil.rmtree(destination)

    # -------------------------------------------------------------------------
    # Copy the COMPLETE project (Ignoring .ipynb files)
    # -------------------------------------------------------------------------

    print(
        "    Copying source directory (skipping .ipynb files)..."
    )

    shutil.copytree(
        SOURCE_DIR,
        destination,
        ignore=shutil.ignore_patterns('*.ipynb'),
    )

    # -------------------------------------------------------------------------
    # Modify ONLY the copied config
    # -------------------------------------------------------------------------

    config_path = destination / CONFIG_RELATIVE

    if not config_path.is_file():

        raise RuntimeError(
            f"Expected config was not found:\n"
            f"    {config_path}"
        )

    configure_case(
        config_path=config_path,
        hydro=hydro,
        method=method,
        loss_function=loss_function,
        w1=w1,
        w2=w2,
        weight_tag=weight_tag,
    )

    print(
        "    Config updated successfully."
    )

    return destination


# =============================================================================
# MAIN
# =============================================================================

def main() -> int:

    parser = argparse.ArgumentParser(
        description=(
            "Create independent DPL experiment directories with temporal splits."
        )
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help=(
            "Delete and recreate existing experiment directories."
        ),
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Show all cases without copying or modifying anything."
        ),
    )

    args = parser.parse_args()

    # =========================================================================
    # CHECK SOURCE
    # =========================================================================

    if not SOURCE_DIR.is_dir():

        print(
            "ERROR: source directory does not exist:"
        )

        print(
            f"    {SOURCE_DIR}"
        )

        return 1

    source_config = SOURCE_DIR / CONFIG_RELATIVE

    if not source_config.is_file():

        print(
            "ERROR: source config does not exist:"
        )

        print(
            f"    {source_config}"
        )

        return 1

    # =========================================================================
    # BUILD EXPERIMENT LIST
    # =========================================================================

    experiments = []

    for method in METHOD_FORCING_PATHS:

        for hydro in HYDRO_MODELS:

            for loss_function in LOSS_FUNCTIONS:

                for w1, w2, weight_tag in WEIGHT_COMBINATIONS:

                    experiments.append(
                        {
                            "method": method,
                            "hydro": hydro,
                            "loss_function": loss_function,
                            "w1": w1,
                            "w2": w2,
                            "weight_tag": weight_tag,
                        }
                    )

    # =========================================================================
    # EXPECTED NUMBER
    # =========================================================================

    expected = (
        len(METHOD_FORCING_PATHS)
        * len(HYDRO_MODELS)
        * len(LOSS_FUNCTIONS)
        * len(WEIGHT_COMBINATIONS)
    )

    assert len(experiments) == expected

    # =========================================================================
    # HEADER
    # =========================================================================

    print()
    print("=" * 90)
    print("DPL EXPERIMENT GENERATOR (TEMPORAL TEST)")
    print("=" * 90)

    print()
    print("Source directory:")
    print(
        f"    {SOURCE_DIR}"
    )

    print()
    print("Destination root:")
    print(
        f"    {DPL_ROOT}"
    )

    print()
    print("Temporal Splits:")
    print(f"    tRange   : {TEMPORAL_CONFIG['tRange']}")
    print(f"    t_train  : {TEMPORAL_CONFIG['t_train']}")
    print(f"    t_test   : {TEMPORAL_CONFIG['t_test']}")

    print()
    print("Methods:")
    for method in METHOD_FORCING_PATHS:
        print(
            f"    {method}"
        )

    print()
    print("Hydro models:")
    for hydro in HYDRO_MODELS:
        print(
            f"    {hydro}"
        )

    print()
    print("Loss functions:")
    for loss in LOSS_FUNCTIONS:
        print(
            f"    {loss}"
        )

    print()
    print("Weights:")

    for w1, w2, tag in WEIGHT_COMBINATIONS:

        print(
            f"    {tag}: w1={w1}, w2={w2}"
        )

    print()
    print(
        f"TOTAL CASES: {len(experiments)}"
    )

    print("=" * 90)

    # =========================================================================
    # CREATE CASES
    # =========================================================================

    for i, exp in enumerate(
        experiments,
        start=1,
    ):

        print()
        print(
            f"[{i:03d}/{len(experiments):03d}]"
        )

        destination = DPL_ROOT / case_relative_path(
            method=exp["method"],
            hydro=exp["hydro"],
            loss_function=exp["loss_function"],
            weight_tag=exp["weight_tag"],
        )

        # ---------------------------------------------------------------------
        # Dry run
        # ---------------------------------------------------------------------

        if args.dry_run:

            print(
                f"    {destination}"
            )

            print(
                f"    forcing = "
                f"{METHOD_FORCING_PATHS[exp['method']]}"
            )

            print(
                f"    w1={exp['w1']}, "
                f"w2={exp['w2']}"
            )

            output_model_path = f"/home/s0shar47/scratch/salil/DPL/CASES/{exp['method']}/{exp['hydro']}/{exp['loss_function']}/{exp['weight_tag']}/OUTPUTS/"
            print(
                f"    output_model = "
                f"{output_model_path}"
            )

            continue

        # ---------------------------------------------------------------------
        # Create
        # ---------------------------------------------------------------------

        try:

            create_case(
                method=exp["method"],
                hydro=exp["hydro"],
                loss_function=exp["loss_function"],
                w1=exp["w1"],
                w2=exp["w2"],
                weight_tag=exp["weight_tag"],
                overwrite=args.overwrite,
            )

        except Exception as exc:

            print()
            print(
                "!!! ERROR CREATING CASE !!!"
            )

            print(
                f"    {destination}"
            )

            print(
                f"    {exc}"
            )

            return 1

    # =========================================================================
    # FINISHED
    # =========================================================================

    print()
    print("=" * 90)

    if args.dry_run:

        print(
            "DRY RUN COMPLETE"
        )

        print(
            f"Would create: {len(experiments)} cases"
        )

    else:

        print(
            "CASE GENERATION COMPLETE"
        )

        print(
            f"Created/verified: {len(experiments)} cases"
        )

    print("=" * 90)

    return 0


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    raise SystemExit(
        main()
    )