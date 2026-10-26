#!/bin/bash

cd "/home/s0shar47/scratch/salil/DPL/dPL_Hydro_SNTEMP"

export CUDA_VISIBLE_DEVICES=1

echo "============================================================"
echo "SCREEN JOB STARTED"
echo "============================================================"
echo "Job        : 10"
echo "Region     : Region_4"
echo "Model      : HBV"
echo "GPU        : 1"
echo "Screen     : PUR_R4_RMSE_LocalHYSEPHBV"
echo "Start time : $(date)"
echo "============================================================"

"python3" "/home/s0shar47/scratch/salil/DPL/dPL_Hydro_SNTEMP/RUN_21_JOBS/job_10_R4_HBV_LocalHYSEP_RMSE.py"

EXIT_CODE=$?

echo ""
echo "============================================================"
echo "JOB FINISHED"
echo "============================================================"
echo "Job        : 10"
echo "Region     : Region_4"
echo "Model      : HBV"
echo "Exit code  : $EXIT_CODE"
echo "Time       : $(date)"
echo "============================================================"

exit $EXIT_CODE
