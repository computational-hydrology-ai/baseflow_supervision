import os
import sys
import traceback

# ------------------------------------------------------------
# Make sure we are running from the DPL repository
# ------------------------------------------------------------

REPO_DIR = r"/home/s0shar47/scratch/salil/DPL/dPL_Hydro_SNTEMP"

os.chdir(REPO_DIR)

if REPO_DIR not in sys.path:
    sys.path.insert(0, REPO_DIR)


# ------------------------------------------------------------
# Import your existing main program
# ------------------------------------------------------------

from main_hydro_temp import main_hydro_temp

# Import the ORIGINAL configuration dictionary
from config.read_configurations import config_hydro_temp


# ------------------------------------------------------------
# Make an independent copy of the configuration
# ------------------------------------------------------------

args = dict(config_hydro_temp)


# ============================================================
# EXPERIMENT INFORMATION
# ============================================================

REGION = 1
MODEL = "HBV_capillary"

# TRAIN_FORCING = r"/scratch/data/PUR_DATA/train/Region_1/daymet_19800101_20141231_forcing_671.npy"
# TRAIN_ATTR = r"/scratch/data/PUR_DATA/train/Region_1/daymet_19800101_20141231_attr_671.npy"

TEST_FORCING = r"/scratch/data/PUR_DATA/test/Region_1/daymet_19800101_20141231_forcing_671.npy"
TEST_ATTR = r"/scratch/data/PUR_DATA/test/Region_1/daymet_19800101_20141231_attr_671.npy"

OUTPUT_MODEL = r"/home/s0shar47/scratch/OUTPUTS_Paper1v2/PUR/Single/NSE/HBV_capillary/Region_1"

STATUS_FILE = r"/home/s0shar47/scratch/salil/DPL/dPL_Hydro_SNTEMP/RUN_21_JOBS/status/job_02.status"


# ============================================================
# COMMON SETTINGS
# ============================================================

args["randomseed"] = [111111]

args['Action'] = [1]

args["device"] = "cuda"

args["nmul"] = 16

args["NN_model_name"] = "LSTM"


args["tRange"] = [19800101, 20141231]

args["t_train"] = [19891001, 19990930]

# args["t_test"] = [19891001, 19990930]

args["t_test"] = [19800101, 20141231]


# args["loss_function"] = "RmseLoss_4items"

# args["loss_function"] = "NseLoss_flow_baseflow"


args["loss_function"] = "NSEsqrtLoss_flow"

args["loss_function_weights"] = {
    "w1": 0.5,
    "w2": 0.5
}

args["target"] = [
    "00060_Mean",
    # "baseflow"
]


args["warm_up"] = 365

args["rho"] = 365

args["batch_size"] = 100

args["EPOCHS"] = 50

args["EPOCH_testing"] = 50

args["hidden_size"] = 256

args["dropout"] = 0.5

args["saveEpoch"] = 10

args["no_basins"] = 25


# ============================================================
# NN INPUTS
# ============================================================

args["varT_NN"] = [
    "prcp(mm/day)",
    "tmean(C)",
    "PEVAP"
]


args["varC_NN"] = [

    "p_mean",
    "pet_mean",
    "p_seasonality",
    "frac_snow",
    "aridity",

    "high_prec_freq",
    "high_prec_dur",
    "low_prec_freq",
    "low_prec_dur",

    "elev_mean",
    "slope_mean",
    "area_gages2",
    "frac_forest",
    "lai_max",

    "lai_diff",
    "gvf_max",
    "gvf_diff",

    "dom_land_cover_frac",
    "dom_land_cover",

    "root_depth_50",
    "soil_depth_pelletier",

    "soil_depth_statsgo",
    "soil_porosity",
    "soil_conductivity",

    "max_water_content",
    "sand_frac",
    "silt_frac",
    "clay_frac",

    "geol_1st_class",
    "glim_1st_class_frac",

    "geol_2nd_class",
    "glim_2nd_class_frac",

    "carbonate_rocks_frac",
    "geol_porostiy",
    "geol_permeability"
]


args["varT_hydro_model"] = [
    "prcp(mm/day)",
    "tmean(C)",
    "PEVAP"
]

args["varC_hydro_model"] = [
    "area_gages2"
]


args["dydrop"] = 0.0

args["routing_hydro_model"] = True


# ============================================================
# PET
# ============================================================

args["potet_module"] = "dataset"

args["potet_dataset_name"] = "PEVAP"


# ============================================================
# HYDRO MODEL
# ============================================================

args["hydro_model_name"] = MODEL


if MODEL == "HBV":

    args["dyn_params_list_hydro"] = [
        "parBETA",
        "parBETAET"
    ]


elif MODEL == "HBV_capillary":

    args["dyn_params_list_hydro"] = [
        "parBETA",
        "parK0",
        "parUZL",
        "parBETAET"
    ]


elif MODEL == "marrmot_PRMS":

    args["dyn_params_list_hydro"] = [
        "scx",
        "cgw",
        "alpha",
        "tt"
    ]


else:

    raise ValueError(
        f"Unknown hydro model: {MODEL}"
    )


# ============================================================
# OUTPUT DIRECTORY
# ============================================================

args["output_model"] = OUTPUT_MODEL

os.makedirs(
    OUTPUT_MODEL,
    exist_ok=True
)


# ============================================================
# 1. TRAIN
# ============================================================

# try:

#     print("=" * 80)
#     print("TRAINING")
#     print("=" * 80)

#     print("Region :", REGION)
#     print("Model  :", MODEL)
#     print("GPU    :", os.environ.get("CUDA_VISIBLE_DEVICES"))
#     print()

#     args["Action"] = [0]

#     args["forcing_path"] = TRAIN_FORCING

#     args["attr_path"] = TRAIN_ATTR

#     print("Action        :", args["Action"])
#     print("Forcing       :", args["forcing_path"])
#     print("Attributes    :", args["attr_path"])
#     print("Output        :", args["output_model"])
#     print()

#     main_hydro_temp(args)

#     print()
#     print("=" * 80)
#     print("TRAINING COMPLETED")
#     print("=" * 80)
#     print()


# except Exception as e:

#     print()
#     print("=" * 80)
#     print("TRAINING FAILED")
#     print("=" * 80)

#     traceback.print_exc()

#     with open(
#         STATUS_FILE,
#         "w"
#     ) as f:
#         f.write("TRAIN_FAILED\n")

#     raise


# ============================================================
# 2. TEST
# ============================================================

try:

    print("=" * 80)
    print("TESTING")
    print("=" * 80)

    print("Region :", REGION)
    print("Model  :", MODEL)
    print("GPU    :", os.environ.get("CUDA_VISIBLE_DEVICES"))
    print()

    args["Action"] = [1]

    args["forcing_path"] = TEST_FORCING

    args["attr_path"] = TEST_ATTR

    print("Action        :", args["Action"])
    print("Forcing       :", args["forcing_path"])
    print("Attributes    :", args["attr_path"])
    print("Output        :", args["output_model"])
    print()

    main_hydro_temp(args)

    print()
    print("=" * 80)
    print("TESTING COMPLETED")
    print("=" * 80)
    print()


    # --------------------------------------------------------
    # Mark complete
    # --------------------------------------------------------

    with open(
        STATUS_FILE,
        "w"
    ) as f:
        f.write("DONE\n")


except Exception as e:

    print()
    print("=" * 80)
    print("TESTING FAILED")
    print("=" * 80)

    traceback.print_exc()

    with open(
        STATUS_FILE,
        "w"
    ) as f:
        f.write("TEST_FAILED\n")

    raise
