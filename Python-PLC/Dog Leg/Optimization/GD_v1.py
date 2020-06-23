import numpy as np
import pandas as pd
import scipy.optimize as sp
import matplotlib.pyplot as plt
from Master import FWHM
from plot_functions import plot_traj, plot_scatter
from read_dogleg import read_dogleg, gen_perturb_scan


###############################################################################
# User input values:
# directory
# fname
# step_size (amount to perturb the y-intercept values)
# n_step (number of sampling points for the perturbed beam trajectories)
# limits (start and end points for WF6x and WF6y for the newly sampled data)


def linear_fit(x,a,b):
    return a + b*x

###############################################################################
# Initialize variables to be kept track of
horz_fwhm = np.zeros(1)
vert_fwhm = np.zeros(1)
horz_yint = np.zeros(1)
vert_yint = np.zeros(1)
horz_slope = np.zeros(1)
vert_slope = np.zeros(1)
fom = np.zeros(1)

###############################################################################
# Initialize plotting figures and axes
x_fit = np.linspace(-5,5, 1000) # for plotting fit curves

# For plotting horizontal and vertical scan trajectories
fig1 = plt.figure()
ax11 = fig1.add_subplot(121); ax12 = fig1.add_subplot(122)

# For plotting FOM as function of y-intercepts
fig2 = plt.figure()
ax2 = fig2.add_subplot(111)

###############################################################################
# Import data and calculate variables of interest
directory = './data/'
fname = directory + '200604_1437.txt'

horz_fwhm[0],  vert_fwhm[0],\
horz_yint[0],  vert_yint[0], \
horz_slope[0], vert_slope[0], \
horz,          vert, \
fom[0] =  read_dogleg(fname, linear_fit)


###############################################################################
# Generate plots

# Plot trajectories of horizontal and vertical scans
plot_traj((ax11, ax12), x_fit, linear_fit, horz, vert, 
          (horz_yint, horz_slope), (vert_yint, vert_slope))

# Plot scatter plot of FOM
plot_scatter(fig2, ax2, horz_yint, vert_yint, fom)


###############################################################################
# Generate new y-intercept values for the next two measurements that we want to take
# Use step size 0.002 for our step size in both axes

step_size = 0.01
# Perturb horizontal scan
horz_yint = np.append(horz_yint, horz_yint[0] + step_size); vert_yint = np.append(vert_yint, vert_yint[0])
# Perturb vertical scan
vert_yint = np.append(vert_yint, vert_yint[0] + step_size); horz_yint = np.append(horz_yint, horz_yint[0])

# Plot the new points
plot_scatter(fig2, ax2, horz_yint, vert_yint, fom, perturb=True)

###############################################################################
# Generate the WF6 and WF7 vectors needed to perform the scans
# Check with Austin how he generates these input vectors

nstep = 40    
#limits order:  (x_start   x_stop  y_start  y_stop)
limits = (0, -0.35, -0.4, -0.75)

# Perturbed in horizontal direction
wf6x, wf7x, wf6y, wf7y, df_x = gen_perturb_scan(nstep, linear_fit, limits, 
                                               horz_yint, vert_yint, 
                                               horz_slope, vert_slope,
                                               horz, vert, 'horz')
# plot to show the new trajectories
ax11.plot(wf6x, wf7x, 'o', markersize=3, color='magenta')
ax12.plot(wf6y, wf7y, 'o', markersize=3, color='magenta')
#


# Perturbed in the vertical direction
wf6x, wf7x, wf6y, wf7y, df_y = gen_perturb_scan(nstep, linear_fit, limits, 
                                               horz_yint, vert_yint, 
                                               horz_slope, vert_slope,
                                               horz, vert, 'vert')
# plot to show the new trajectories
ax11.plot(wf6x, wf7x, 'o', markersize=3, color='darkgoldenrod')
ax12.plot(wf6y, wf7y, 'o', markersize=3, color='darkgoldenrod')



###############################################################################
# Check the dataframe variables
fig_p = plt.figure()
ax_ph = fig_p.add_subplot(121)
ax_pv = fig_p.add_subplot(122)

# plot initial scan trajecty
ax_ph.plot(horz[:,0], horz[:,1], color='blue', label='base case')
ax_pv.plot(vert[:,2], vert[:,3], color='red', label='base case')

# Plot horizontal perturbed scan
ax_ph.plot(df_x['WF6x'][0:40], df_x['WF7x'][0:40], marker='o', color='magenta', label='horz perturb')
ax_pv.plot(df_x['WF6y'][40:], df_x['WF7y'][40:], marker='o', color='magenta', label='horz perturb')

# Plot vertical perturbed scan
ax_ph.plot(df_y['WF6x'][0:40], df_y['WF7x'][0:40], marker='o', color='darkgoldenrod', label='vert perturb')
ax_pv.plot(df_y['WF6y'][40:], df_y['WF7y'][40:], marker='o', color='darkgoldenrod', label='vert perturb')

# Labels and stuff
ax_ph.set_xlabel('WF6x (A)'); ax_ph.set_ylabel('WF7x (A)')
ax_ph.set_title('Horizontal scan trajectory')
ax_ph.axhline(0, color='black'); ax_ph.axvline(0, color='black')
ax_ph.grid(b='True', axis='both')
ax_ph.legend()


ax_pv.set_xlabel('WF6y (A)'); ax_pv.set_ylabel('WF7y (A)')
ax_pv.set_title('Horizontal scan trajectory')
ax_pv.axhline(0, color='black'); ax_pv.axvline(0, color='black')
ax_pv.grid(b='True', axis='both')
ax_pv.legend()


###############################################################################
# Write to perturbed dfs to .csv file
s_name = fname[:-4] + '_perturub_horz.txt'
df_x.to_csv(s_name, index=False, sep='\t',
            columns=['WF6x', 'WF7x', 'WF6y', 'WF7y'], 
            header= ['WF6x    ', 'WF7x    ', 'WF6y    ', 'WF7y    '], float_format='%.6f')

s_name = fname[:-4] + '_perturub_vert.txt'
df_y.to_csv(s_name, index=False, sep='\t',
            columns=['WF6x', 'WF7x', 'WF6y', 'WF7y'], 
            header= ['WF6x    ', 'WF7x    ', 'WF6y    ', 'WF7y    '], float_format='%.6f')

plt.show()
###############################################################################
# Relevent to my interests

print('Figure of merit (FOM)= FWHM_x^2 + FWHM_y^2$')
print('Maximum FOM = 0.384^2 * 2 = ' + str(0.2949) + ' A^2')
print('FOM of the initial scan = %.4f' %fom[0] + ' A^2')
print('Let us use dx = %.3f and dy =%.3f for our step size in GD' %(step_size, step_size))
print('The y-intercept values for the initial scan: \
    ax = %.3f, ay = %.3f' %(horz_yint[0], vert_yint[0]))
print('The y-intercept values for the horizontal perturbed scan: \
    ax = %.3f, ay = %.3f' %(horz_yint[1], vert_yint[1]))
print('The y-intercept values for the vertical perturbed scan: \
    ax = %.3f, ay = %.3f' %(horz_yint[2], vert_yint[2]))
