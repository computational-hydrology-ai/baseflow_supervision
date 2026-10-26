#!/bin/bash

cd "/home/s0shar47/scratch/salil/DPL/dPL_Hydro_SNTEMP"

export CUDA_VISIBLE_DEVICES=1

echo "============================================================"
echo "SCREEN JOB STARTED"
echo "============================================================"
echo "Job        : 02"
echo "Region     : Region_1"
echo "Model      : HBV_capillary"
echo "GPU        : 1"
echo "Screen     : PUR_R1_RMSE_LocalHYSEPHBV_capillary"
echo "Start time : $(date)"
echo "============================================================"

"python3" "/home/s0shar47/scratch/salil/DPL/dPL_Hydro_SNTEMP/RUN_21_JOBS/job_02_R1_HBV_capillary_LocalHYSEP_RMSE.py"

EXIT_CODE=$?

echo ""
echo "============================================================"
echo "JOB FINISHED"
echo "============================================================"
echo "Job        : 02"
echo "Region     : Region_1"
echo "Model      : HBV_capillary"
echo "Exit code  : $EXIT_CODE"
echo "Time       : $(date)"
echo "============================================================"

exit $EXIT_CODE
