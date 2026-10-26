#!/usr/bin/env python3

import os
import time
import subprocess
from pathlib import Path

method='LocalHYSEP'
loss='RMSE'
# ============================================================
# PATHS
# ============================================================



REPO_DIR = "/home/s0shar47/scratch/salil/DPL/dPL_Hydro_SNTEMP"

MAIN_SCRIPT = os.path.join(
    REPO_DIR,
    "main_hydro_temp.py"
)

# Your existing configuration module
CONFIG_MODULE = "config.read_configurations"

# Existing input data
TRAIN_BASE = "/scratch/data/PUR_DATA/train"
TEST_BASE = "/scratch/data/PUR_DATA/test"

# Output base
OUTPUT_BASE = (
    "/home/s0shar47/scratch/OUTPUTS_Paper1v2/"
    F"PUR/{method}_Multi/{loss}"
)

# Where generated launcher scripts will be stored
RUN_DIR = os.path.join(
    REPO_DIR,
    "RUN_21_JOBS"
)

LOG_DIR = os.path.join(
    RUN_DIR,
    "logs"
)

STATUS_DIR = os.path.join(
    RUN_DIR,
    "status"
)


# ============================================================
# EXECUTION SETTINGS
# ============================================================

PYTHON = "python3"

GPUS = [0, 1]

# 5 jobs per GPU = 10 jobs total
JOBS_PER_GPU = 1

MAX_PARALLEL_JOBS = 2

# Check every 30 seconds
CHECK_INTERVAL = 30


# ============================================================
# EXPERIMENT SETTINGS
# ============================================================

REGIONS = range(1, 8)

MODELS = [
    "HBV",
    "HBV_capillary",
    "marrmot_PRMS",
]


# ============================================================
# MODEL-SPECIFIC DYNAMIC PARAMETERS
# ============================================================

DYN_PARAMS = {

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


# ============================================================
# CREATE DIRECTORIES
# ============================================================

Path(RUN_DIR).mkdir(
    parents=True,
    exist_ok=True
)

Path(LOG_DIR).mkdir(
    parents=True,
    exist_ok=True
)

Path(STATUS_DIR).mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# JOB LIST
# ============================================================

JOBS = []

job_id = 0

for region in REGIONS:

    for model in MODELS:

        job_id += 1

        JOBS.append({
            "job_id": job_id,
            "region": region,
            "model": model
        })


# ============================================================
# PRINT JOB LIST
# ============================================================

print()
print("=" * 90)
print("21-JOB PUR HYDROLOGIC EXPERIMENT")
print("=" * 90)

for job in JOBS:

    print(
        f"JOB {job['job_id']:02d} : "
        f"Region_{job['region']}_{loss}_{method}: "
        f"{job['model']}"
    )

print("=" * 90)
print()


# ============================================================
# SCREEN NAME
# ============================================================

def get_screen_name(job):

    return (
        f"PUR_R{job['region']}_{loss}_{method}"
        f"{job['model']}"
    )


# ============================================================
# JOB SCRIPT NAME
# ============================================================

def get_job_script(job):

    return os.path.join(
        RUN_DIR,
        f"job_{job['job_id']:02d}_"
        f"R{job['region']}_"
        f"{job['model']}_{method}_{loss}.py"
    )


# ============================================================
# LOG FILE
# ============================================================

def get_log_file(job):

    return os.path.join(
        LOG_DIR,
        f"job_{job['job_id']:02d}_"
        f"R{job['region']}_"
        f"{job['model']}_{method}_{loss}.log"
    )


# ============================================================
# STATUS FILE
# ============================================================

def get_status_file(job):

    return os.path.join(
        STATUS_DIR,
        f"job_{job['job_id']:02d}.status"
    )


# ============================================================
# CREATE PYTHON LAUNCHER FOR ONE REGION + MODEL
# ============================================================

def create_job_script(job):

    region = job["region"]
    model = job["model"]

    forcing_train = (
        f"{TRAIN_BASE}/Region_{region}/"
        f"daymet_19800101_20141231_"
        f"forcing_671_LocalHYSEP_mmday.npy"
    )



    attr_train = (
        f"{TRAIN_BASE}/Region_{region}/"
        f"daymet_19800101_20141231_"
        f"attr_671.npy"
    )

    forcing_test = (
        f"{TEST_BASE}/Region_{region}/"
        f"daymet_19800101_20141231_"
        f"forcing_671_LocalHYSEP_mmday.npy"
    )

    attr_test = (
        f"{TEST_BASE}/Region_{region}/"
        f"daymet_19800101_20141231_"
        f"attr_671.npy"
    )


    output_model = os.path.join(
        OUTPUT_BASE,
        model,
        f"Region_{region}"
    )



    status_file = get_status_file(job)

    script_path = get_job_script(job)

    # --------------------------------------------------------
    # Python script
    #
    # IMPORTANT:
    # This imports your EXISTING main_hydro_temp.py.
    # No changes are made to main_hydro_temp.py.
    # --------------------------------------------------------

    script = f'''import os
import sys
import traceback

# ------------------------------------------------------------
# Make sure we are running from the DPL repository
# ------------------------------------------------------------

REPO_DIR = r"{REPO_DIR}"

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

REGION = {region}
MODEL = "{model}"

# TRAIN_FORCING = r"{forcing_train}"
# TRAIN_ATTR = r"{attr_train}"

TEST_FORCING = r"{forcing_test}"
TEST_ATTR = r"{attr_test}"

OUTPUT_MODEL = r"{output_model}"

STATUS_FILE = r"{status_file}"


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


args["loss_function"] = "RmseLoss_4items"

# args["loss_function"] = "NseLoss_flow_baseflow"


# args["loss_function"] = "NSEsqrtLoss_flow"

args["loss_function_weights"] = {{
    "w1": 0.5,
    "w2": 0.5
}}

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
        f"Unknown hydro model: {{MODEL}}"
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
#         f.write("TRAIN_FAILED\\n")

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
        f.write("DONE\\n")


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
        f.write("TEST_FAILED\\n")

    raise
'''

    with open(script_path, "w") as f:
        f.write(script)

    return script_path


# ============================================================
# CREATE SHELL SCRIPT FOR SCREEN
# ============================================================

def create_shell_script(job, gpu):

    job_script = create_job_script(job)

    log_file = get_log_file(job)

    status_file = get_status_file(job)

    screen_name = get_screen_name(job)

    shell_path = os.path.join(
        RUN_DIR,
        f"run_{job['job_id']:02d}.sh"
    )

    shell_script = f"""#!/bin/bash

cd "{REPO_DIR}"

export CUDA_VISIBLE_DEVICES={gpu}

echo "============================================================"
echo "SCREEN JOB STARTED"
echo "============================================================"
echo "Job        : {job['job_id']:02d}"
echo "Region     : Region_{job['region']}"
echo "Model      : {job['model']}"
echo "GPU        : {gpu}"
echo "Screen     : {screen_name}"
echo "Start time : $(date)"
echo "============================================================"

"{PYTHON}" "{job_script}"

EXIT_CODE=$?

echo ""
echo "============================================================"
echo "JOB FINISHED"
echo "============================================================"
echo "Job        : {job['job_id']:02d}"
echo "Region     : Region_{job['region']}"
echo "Model      : {job['model']}"
echo "Exit code  : $EXIT_CODE"
echo "Time       : $(date)"
echo "============================================================"

exit $EXIT_CODE
"""

    with open(shell_path, "w") as f:
        f.write(shell_script)

    os.chmod(
        shell_path,
        0o755
    )

    return shell_path


# ============================================================
# SCREEN EXISTS?
# ============================================================

def screen_exists(session):

    result = subprocess.run(
        ["screen", "-ls"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True
    )

    return session in result.stdout


# ============================================================
# START JOB
# ============================================================

def start_job(job, gpu):

    session = get_screen_name(job)

    shell_script = create_shell_script(
        job,
        gpu
    )

    log_file = get_log_file(job)

    # Remove old status
    status_file = get_status_file(job)

    if os.path.exists(status_file):
        os.remove(status_file)

    print(
        f"STARTING "
        f"JOB {job['job_id']:02d} | "
        f"Region_{job['region']} | "
        f"{job['model']} | "
        f"GPU {gpu}"
    )

    # --------------------------------------------------------
    # Start detached screen
    # --------------------------------------------------------

    command = [
        "screen",
        "-dmS",
        session,
        "bash",
        "-c",
        f'bash "{shell_script}" > "{log_file}" 2>&1'
    ]

    subprocess.Popen(command)

    time.sleep(2)

    if screen_exists(session):

        print(
            f"    screen started: {session}"
        )

    else:

        print(
            f"    WARNING: screen did not start: "
            f"{session}"
        )


# ============================================================
# JOB COMPLETE?
# ============================================================

def job_finished(job):

    status_file = get_status_file(job)

    return os.path.exists(status_file)


# ============================================================
# GET STATUS
# ============================================================

def get_status(job):

    status_file = get_status_file(job)

    if not os.path.exists(status_file):
        return "RUNNING"

    with open(status_file, "r") as f:

        return f.read().strip()


# ============================================================
# WAIT FOR BATCH
# ============================================================

def wait_for_batch(batch):

    print()
    print("=" * 90)
    print("WAITING FOR BATCH")
    print("=" * 90)

    while True:

        finished = 0

        for job in batch:

            if job_finished(job):
                finished += 1

        running = len(batch) - finished

        print(
            f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] "
            f"Finished: {finished}/{len(batch)} | "
            f"Running: {running}"
        )

        # ----------------------------------------------------
        # Print current jobs
        # ----------------------------------------------------

        for job in batch:

            status = get_status(job)

            print(
                f"    JOB {job['job_id']:02d} | "
                f"Region_{job['region']} | "
                f"{job['model']} | "
                f"{status}"
            )

        print()

        if finished == len(batch):

            break

        time.sleep(CHECK_INTERVAL)

    print(
        "BATCH COMPLETE"
    )

    print()


# ============================================================
# LAUNCH BATCH
# ============================================================

def launch_batch(batch):

    print()
    print("=" * 90)
    print(
        f"LAUNCHING {len(batch)} JOBS"
    )
    print("=" * 90)

    for i, job in enumerate(batch):

        # ----------------------------------------------------
        # Jobs 0-4 -> GPU 0
        # Jobs 5-9 -> GPU 1
        # ----------------------------------------------------

        gpu_index = i // JOBS_PER_GPU

        gpu = GPUS[gpu_index]

        start_job(
            job,
            gpu
        )

    print()
    print(
        "All jobs in this batch have been submitted."
    )
    print()


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 90)
    print("PUR 21-JOB TRAIN + TEST RUNNER")
    print("=" * 90)

    print(
        f"Repository      : {REPO_DIR}"
    )

    print(
        f"Main script     : {MAIN_SCRIPT}"
    )

    print(
        f"Total jobs      : {len(JOBS)}"
    )

    print(
        f"Parallel jobs   : {MAX_PARALLEL_JOBS}"
    )

    print(
        f"GPU 0 jobs      : {JOBS_PER_GPU}"
    )

    print(
        f"GPU 1 jobs      : {JOBS_PER_GPU}"
    )

    print("=" * 90)
    print()


    # ========================================================
    # DELETE OLD STATUS FILES
    # ========================================================

    for filename in os.listdir(STATUS_DIR):

        path = os.path.join(
            STATUS_DIR,
            filename
        )

        if os.path.isfile(path):

            os.remove(path)


    # ========================================================
    # CREATE BATCHES
    # ========================================================

    batches = []

    for i in range(
        0,
        len(JOBS),
        MAX_PARALLEL_JOBS
    ):

        batches.append(
            JOBS[
                i:i + MAX_PARALLEL_JOBS
            ]
        )


    print(
        f"Number of batches: {len(batches)}"
    )

    for i, batch in enumerate(
        batches,
        start=1
    ):

        print(
            f"    Batch {i}: "
            f"{len(batch)} jobs"
        )

    print()


    # ========================================================
    # RUN BATCHES
    # ========================================================

    for batch_number, batch in enumerate(
        batches,
        start=1
    ):

        print()
        print("#" * 90)
        print(
            f"BATCH {batch_number}/{len(batches)}"
        )
        print("#" * 90)

        launch_batch(batch)

        wait_for_batch(batch)


    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print()
    print("=" * 90)
    print("ALL 21 JOBS HAVE FINISHED")
    print("=" * 90)
    print()

    print(
        "Final job status:"
    )

    print()

    for job in JOBS:

        status = get_status(job)

        print(
            f"JOB {job['job_id']:02d} | "
            f"Region_{job['region']} | "
            f"{job['model']} | "
            f"{status}"
        )

    print()
    print("=" * 90)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()