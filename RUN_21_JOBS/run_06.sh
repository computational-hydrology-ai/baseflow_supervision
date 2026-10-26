#!/bin/bash

cd "/home/s0shar47/scratch/salil/DPL/dPL_Hydro_SNTEMP"

export CUDA_VISIBLE_DEVICES=1

echo "============================================================"
echo "SCREEN JOB STARTED"
echo "============================================================"
echo "Job        : 06"
echo "Region     : Region_2"
echo "Model      : marrmot_PRMS"
echo "GPU        : 1"
echo "Screen     : PUR_R2_RMSE_LocalHYSEPmarrmot_PRMS"
echo "Start time : $(date)"
echo "============================================================"

"python3" "/home/s0shar47/scratch/salil/DPL/dPL_Hydro_SNTEMP/RUN_21_JOBS/job_06_R2_marrmot_PRMS_LocalHYSEP_RMSE.py"

EXIT_CODE=$?

echo ""
echo "============================================================"
echo "JOB FINISHED"
echo "============================================================"
echo "Job        : 06"
echo "Region     : Region_2"
echo "Model      : marrmot_PRMS"
echo "Exit code  : $EXIT_CODE"
echo "Time       : $(date)"
echo "============================================================"

exit $EXIT_CODE
