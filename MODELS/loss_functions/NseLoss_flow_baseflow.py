import torch
import numpy as np
import json
import os

class NseLoss_flow_baseflow(torch.nn.Module):
    def __init__(self, stdarray_flow, stdarray_baseflow, w1=3, w2=1, alpha=0.25, eps=0.1):
        super(NseLoss_flow_baseflow, self).__init__()
        self.std_flow = stdarray_flow
        self.std_baseflow = stdarray_baseflow
        self.w1 = w1
        self.w2 = w2
        self.alpha = alpha  # weight between standard RMSE-style NSE and log-transformed NSE
        self.eps = eps

    def forward(self, args, y_sim, y_obs, igrid):
        if self.w2 is None:
            self.w2 = 1 - self.w1

        varTar_NN = args["target"]
        obs_flow = y_obs[:, :, varTar_NN.index("00060_Mean")]
        obs_baseflow = y_obs[:, :, varTar_NN.index("baseflow")]
        
        sim_flow = y_sim["flow_sim"].squeeze()
        sim_baseflow = y_sim["gwflow"].squeeze()

        # -----------------------------------------------------------------
        # 1. Flow NSE Loss (Combined standard & log-transformed NSE)
        # -----------------------------------------------------------------
        if len(obs_flow[obs_flow == obs_flow]) > 0:
            nt = obs_flow.shape[0]
            
            # Streamflow standard deviation mapping for normalization
            stdse_flow = np.tile(self.std_flow[igrid], (nt, 1))
            stdbatch_flow = torch.tensor(stdse_flow, requires_grad=False).float().to(args["device"])
            
            mask_flow1 = obs_flow == obs_flow
            p = sim_flow[mask_flow1]
            t = obs_flow[mask_flow1]
            stdw_flow = stdbatch_flow[mask_flow1]

            # Normalized squared error for flow (NSE-style denominator)
            sqRes_flow = (p - t) ** 2
            normRes_flow = sqRes_flow / (stdw_flow + self.eps) ** 2
            loss_flow1 = torch.mean(normRes_flow)

            

            loss_flow_total = loss_flow1
        else:
            loss_flow_total = 0.0

        # -----------------------------------------------------------------
        # 2. Baseflow NSE Loss 
        # -----------------------------------------------------------------
        if len(obs_baseflow[obs_baseflow == obs_baseflow]) > 0:
            nt_b = obs_baseflow.shape[0]
            
            # Baseflow standard deviation mapping for normalization
            stdse_baseflow = np.tile(self.std_baseflow[igrid], (nt_b, 1))
            stdbatch_baseflow = torch.tensor(stdse_baseflow, requires_grad=False).float().to(args["device"])
            
            mask_baseflow1 = obs_baseflow == obs_baseflow
            p_baseflow = sim_baseflow[mask_baseflow1]
            t_baseflow = obs_baseflow[mask_baseflow1]
            stdw_baseflow = stdbatch_baseflow[mask_baseflow1]

            # Normalized squared error for baseflow (NSE-style denominator)
            sqRes_baseflow = (p_baseflow - t_baseflow) ** 2
            normRes_baseflow = sqRes_baseflow / (stdw_baseflow + self.eps) ** 2
            
            loss_baseflow = torch.mean(normRes_baseflow)
        else:
            loss_baseflow = 0.0

        # -----------------------------------------------------------------
        # 3. Total Multi-Objective Loss
        # -----------------------------------------------------------------
        loss = self.w1 * loss_flow_total + self.w2 * loss_baseflow 
        return loss