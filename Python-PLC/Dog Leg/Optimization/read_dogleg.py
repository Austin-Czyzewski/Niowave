import pandas as pd
import numpy as np
from Master import FWHM
import scipy.optimize as sp


def read_dogleg(fname, fit_function):
    # This function reads the csv file for a dogleg save and partitions the
    # data into horizontal and vertical scans.
    # Function calculates FWHM for horizontal and vertical scans
    # Function calculates FOM used for optimization
    # Function calculates fit parameters for horizontal and vertical scan trajectories
    
    epsilon = 1e-6 # for partitioning data
    
    ###############################################################################
    # Read data from initial measurement file
    df = pd.read_csv(fname, delimiter=',', header=7) # dataframe containing measured dogleg data
    col = df.columns # column names
    
    ###############################################################################
    # Partition data into horizontal and vertical datasets
    # Use the first column (WF6x) and take difference between adjacent values
    # First index where diff ==0 is the index that divides horizontal and vertical
    # measurement data sets
    
    tmp = df[col[0]].to_numpy()
    diffs = np.abs(tmp[1:] - tmp[:-1])
    sep = np.where(diffs < epsilon)
    sep_index = sep[0]
    
    # Convert to numpy array type
    horz = df.iloc[0:sep_index[0]].to_numpy().astype('float64')
    vert = df.iloc[sep_index[0]:].to_numpy().astype('float64')
    h_current = np.abs(horz[:,5]) + np.abs(horz[:,6])
    v_current = np.abs(vert[:,5]) + np.abs(vert[:,6])
    
    
    ###########################################################################
    # Get FWHM (units: amps)
    _, _, h_fwhm, = FWHM(horz[:,0], h_current, extras=False)
    _, _, v_fwhm, = FWHM(vert[:,2], v_current, extras=False)
    
    ###########################################################################
    # Calculate figure of merit
    fom = np.array([pow(h_fwhm,2) + pow(v_fwhm,2)])
    
    
    ###########################################################################
    # Get fit parameters
    px, _ = sp.curve_fit(fit_function, horz[:,0], horz[:,1])
    py, _ = sp.curve_fit(fit_function, vert[:,2], vert[:,3])
    yint_x = px[0]
    yint_y = py[0]
    slope_x = px[1]
    slope_y = py[1] 
    
    return h_fwhm, v_fwhm, yint_x, yint_y, slope_x, slope_y, horz, vert, fom



def gen_perturb_scan(nstep, fit_function, limits, horz_yint, vert_yint, horz_slope, vert_slope, horz, vert, direction):
    # This function generates the WF6x/WF6y and WF7x/WF7y vectors that are read by the PLC
    # for a perturbed horizontal scan
    # Note: vertical scan trajectory stays the same. Only sampled points are different
    # The limits correspond to WF6x and WF6y values
    # WF7x and WF7y values are calculated from WF6x and WF6y values respectively
    
    ############################
    # For the first measurement#
    x_start = limits[0]        #
    x_end = limits[1]          #
    y_start = limits[2]        #
    y_end = limits[3]          #
    ############################
    
    if direction == 'horz':
        wf6x = np.linspace(min(x_start,x_end), max(x_start,x_end), nstep)
        wf7x = fit_function(wf6x, horz_yint[-2], horz_slope)
        wf6y = np.linspace(min(y_start,y_end), max(y_start,y_end), nstep)
        wf7y = fit_function(wf6y, vert_yint[-2], vert_slope)
    elif direction == 'vert':
        wf6x = np.linspace(min(x_start,x_end), max(x_start,x_end), nstep)
        wf7x = fit_function(wf6x, horz_yint[-1], horz_slope)
        wf6y = np.linspace(min(y_start,y_end), max(y_start,y_end), nstep)
        wf7y = fit_function(wf6y, vert_yint[-1], vert_slope)
    else:
        exit()

    #####################################################
    # Assemble into dataframe variable for easy handling
    # Returns in same order as the initial .csv file
    # Column order: WF6x, WF7x, WF6y, WF7y
    col = ['WF6x', 'WF7x', 'WF6y', 'WF7y']
    
    # Horizontal scan
    df_x = pd.DataFrame(wf6x, columns=[col[0]])
    df_x[col[1]] = wf7x
    # Keep the window frame y-vales of the base case
    df_x[col[2]] = np.ones(nstep)*horz[0,2]
    df_x[col[3]] = np.ones(nstep)*horz[0,3]
    
    # Vertical scan
    # Keep the window fram x-values of the base case
    df_y = pd.DataFrame(np.ones(nstep)*vert[0,0], columns=[col[0]])
    df_y[col[1]] = np.ones(nstep)*vert[0,1]
    df_y[col[2]] = wf6y
    df_y[col[3]] = wf7y
    
    
    df = pd.concat((df_x, df_y), axis=0)

    return wf6x, wf7x, wf6y, wf7y, df
