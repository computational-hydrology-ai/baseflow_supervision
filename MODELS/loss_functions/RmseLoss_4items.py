import torch
import json
import os


class RmseLoss_4items(torch.nn.Module):
    def __init__(self, w1=3, w2=1, alpha=0.25, beta=1e-6):
        super(RmseLoss_4items, self).__init__()
        self.w1 = w1
        self.w2 = w2
        
        self.alpha = alpha  # weights of log-sqrt RMSE
        self.beta = beta

    def forward(self, args, y_sim, y_obs, igrid):
        if self.w2 == None:    # w1 + w2 =1
            self.w2 = 1 - self.w1
        # flow
        varTar_NN = args["target"]
        obs_flow = y_obs[:, :, varTar_NN.index("00060_Mean")]
        obs_baseflow = y_obs[:, :, varTar_NN.index("baseflow")]
        
        sim_flow = y_sim["flow_sim"].squeeze()    #  simulation
        sim_baseflow = y_sim["gwflow"].squeeze()
        

        if len(obs_flow[obs_flow==obs_flow]) > 0:
            mask_flow1 = obs_flow == obs_flow
            p = sim_flow[mask_flow1]
            t = obs_flow[mask_flow1]
            loss_flow1 = torch.sqrt(((p - t) ** 2).mean())  # RMSE item

            p1 = torch.log10(torch.sqrt(sim_flow + self.beta) + 0.1)
            t1 = torch.log10(torch.sqrt(obs_flow + self.beta) + 0.1)

            mask_flow2 = t1 == t1
            pa = p1[mask_flow2]
            ta = t1[mask_flow2]
            loss_flow2 = torch.sqrt(((pa - ta) ** 2).mean())  # Log-Sqrt RMSE item
            loss_flow_total = (1.0-self.alpha) * loss_flow1 + self.alpha * loss_flow2
            # loss_flow_total = loss_flow1 ###Modified to reduce weight of Low flow
        else:
            loss_flow_total = 0.0

        # Baseflow calculation
        if len(obs_baseflow[obs_baseflow==obs_baseflow]) > 0:
            mask_baseflow1 = obs_baseflow == obs_baseflow
            p_baseflow = sim_baseflow[mask_baseflow1]
            t_baseflow = obs_baseflow[mask_baseflow1]

            # p_baseflow2 = torch.where((torch.abs((p_baseflow - t_baseflow)) / (t_baseflow +0.0001) > 0.00), p_baseflow, t_baseflow)
            loss_baseflow1 = torch.sqrt(((p_baseflow - t_baseflow) ** 2).mean())  # RMSE item


            #Log Component for Low baseflow
            pb1= torch.log10(torch.sqrt(sim_baseflow + self.beta)+ 0.1)
            tb1= torch.log10(torch.sqrt(obs_baseflow + self.beta)+ 0.1)

            mask_baseflow2 = tb1 == tb1
            pba = pb1[mask_baseflow2]
            tba = tb1[mask_baseflow2]
            loss_baseflow2 = torch.sqrt(((pba - tba) ** 2).mean())  # Log-Sqrt RMSE item for baseflow

            #Log Component for Low baseflow
            loss_baseflow = (1.0-self.alpha) * loss_baseflow1 + self.alpha * loss_baseflow2

        else:
            loss_baseflow = 0.0

        loss = self.w1 * loss_flow_total + self.w2 * loss_baseflow 
        return loss
