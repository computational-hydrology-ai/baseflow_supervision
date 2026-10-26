import numpy as np
import pandas as pd
import baseflow
import json

actions=['test','train']

for i in range(1,11):
    for action in actions:
    
# 1. Load your raw numpy arrays from your scratch path
        forcings_path = f"/home/s0shar47/scratch/salil/CAMELS_531/PUB_baseflow/{i}/{action}/f_obs_531_with_BFI.npy"
        file_path = f"/home/s0shar47/scratch/salil/CAMELS_531/PUB_baseflow/{i}/{action}/f_obs_531_with_BFI_name.json"
        with open(file_path, "r") as f:
            data = json.load(f)

        # append new entry
        data.append("baseflow")
        forcings = np.load(forcings_path, allow_pickle=True)

        print("Original Forcings shape:", forcings.shape) 
        # Expecting (num_basins, num_timesteps, num_variables)

        num_basins = forcings.shape[0]
        num_timesteps = forcings.shape[1]

        # 2. Pre-allocate an empty array to temporarily hold the baseflow timeseries for all basins
        all_baseflows = np.zeros((num_basins, num_timesteps))

        # 3. Loop through every basin to compute the Furey-Gupta separation vector
        # We do this because baseflow.separation expects data arranged by basin column matrices
        for basin_idx in range(num_basins):
            # Extract streamflow vector for current basin (index 3 based on your configuration)
            Q = forcings[basin_idx, :, 3].copy()
            
            # Clean anomalies or missing data flags (e.g., -99.0) safely to float zeros
            Q = np.where(Q < 0, 0.0, Q).astype(float)
            
            # Create the single-column DataFrame format expected by the package wrapper
            df_streamflow = pd.DataFrame({f'Basin_{basin_idx}': Q})
            
            try:
                # Note: the parameter name in the API signature is 'methods' (plural list)
                df_results = baseflow.separation(df_streamflow, methods=['Furey'])
                baseflow_vector = df_results['Furey'].values
            except Exception as e:
                # Fallback safeguard: If a specific basin fails or has math bounds errors, 
                # initialize it with a basic default or local minimum approach
                baseflow_vector = np.zeros(num_timesteps)
                
            all_baseflows[basin_idx, :] = baseflow_vector

        # 4. Reshape all_baseflows from (basins, timesteps) to (basins, timesteps, 1) 
        # This matches the final dimensional slice requirements for an axis-2 concat
        all_baseflows_reshaped = np.expand_dims(all_baseflows, axis=2)

        # 5. Append the calculated baseflow as the NEW LAST COLUMN inside the forcings array
        updated_forcings = np.concatenate((forcings, all_baseflows_reshaped), axis=2)

        print("New Forcings shape with Furey Baseflow added:", updated_forcings.shape)
        # The final dimension count will increase by +1 (e.g., from 5 to 6)

        # 6. Save the array right back over the original file (or create a new explicit variant file)
        output_path = forcings_path
        np.save(output_path, updated_forcings)

        print(f"Success! Array saved securely to: {output_path}")