#!/bin/bash

cd "/home/s0shar47/scratch/salil/DPL/dPL_Hydro_SNTEMP"

export CUDA_VISIBLE_DEVICES=0

echo "============================================================"
echo "SCREEN JOB STARTED"
echo "============================================================"
echo "Job        : 03"
echo "Region     : Region_1"
echo "Model      : marrmot_PRMS"
echo "GPU        : 0"
echo "Screen     : PUR_R1_RMSE_LocalHYSEPmarrmot_PRMS"
echo "Start time : $(date)"
echo "============================================================"

"python3" "/home/s0shar47/scratch/salil/DPL/dPL_Hydro_SNTEMP/RUN_21_JOBS/job_03_R1_marrmot_PRMS_LocalHYSEP_RMSE.py"

EXIT_CODE=$?

echo ""
echo "============================================================"
echo "JOB FINISHED"
echo "============================================================"
echo "Job        : 03"
echo "Region     : Region_1"
echo "Model      : marrmot_PRMS"
echo "Exit code  : $EXIT_CODE"
echo "Time       : $(date)"
echo "============================================================"

exit $EXIT_CODE
