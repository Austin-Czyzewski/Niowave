import numpy as np
import matplotlib.pyplot as plt
import random
from gd_functions import init_plot, update_plot, final_plot, gd_iteration, converge_v1, converge_v2
import Tag_Database as Tags
import Dog_Leg_Master as M
import datetime
plt.ion()

def f_FOM(x,y):
    D = 20
    L = 1000
    return -(2*pow(D,2) - 2*D*L*(np.abs(x) + np.abs(y)) + pow(L,2)*(x*x + y*y))

###############################################################################
# Initialize updating figures

fig11 = plt.figure(figsize=(14,9))
ax11 = fig11.add_subplot(111)
ax11.set_aspect('equal')


###############################################################################
# Initialize
xmin, xmax, ymin, ymax = -0.019, 0.019, -0.019, 0.019 # these are unused but keep these
limits = (xmin, xmax, ymin, ymax)
alpha = 0.01 # units A^-1

Threshold_Percent = 0
Read_Steps = 20

Client = M.Make_Client('10.50.0.10')

Tag_List = [[Tags.WF6H, False], [Tags.WF7H, False], [Tags.WF6V, False], [Tags.WF7V, False], \
                [Tags.Emitted_Current, True], [Tags.Recirculator_Halfway, True], \
                [Tags.Recirculator_Bypass, True], [Tags.CU_V, False], [Tags.SRF_Pt, False]]

Pulsing_Status = bool(M.Read(Client, Tags.Pulsing_Output, Bool = True)) #Detects whether pulsing or not

if Pulsing_Status:
    count = 25 #Integer. How many points will be recorded at each step and averaged over if pulsing
    sleep_time = 0.010 #Float.(S)
else:
    count = 10 #Non-pulsing count of avg
    sleep_time = 0.010 #Non-pulsing sleep

# Set x_0
x = np.array([M.Read(Client, Tags.WF6H), M.Read(Client, Tags.WF6V)])
print('initial x_0 = [%.3f, %.3f]' %(x[0], x[1]))

# Set f(x_0)

f = M.Dog_Leg(Client, Tags.WF6H, Tags.WF7H, Tags.WF6V, Tags.WF7V, \
              Tags.Recirculator_Bypass, Tags.Recirculator_Halfway, \
              Tag_List, \
              x[0], M.Read(Client, Tags.WF7H), \
              x[1], M.Read(Client, Tags.WF7V), \
              count = count, sleep_time = sleep_time, \
              Threshold_Percent = Threshold_Percent, Read_Steps = Read_Steps)
timestamp = datetime.datetime.now()
print('f(x_0) = %.5f' %f)

# Draw initial point on plot
init_plot(f_FOM, fig11, ax11, x)

# Iteration counter
i = 1

# Measurement counter
m = 1 # start with at least 1 dog leg measurement 


########################################
# For each iteration track:
    # x_k
    # f(x_k)
    # grad(x_k), unit norm
    # ||grad(x_k)||
    # alpha_k
#######################################
x_track = [x]
f_track = [f]
grad_track = []
grad_norm_track= []
alpha_track = [alpha]

# Clean up variables
del x, f, alpha

###############################################################################
# Initialize .log file
fname_log = timestamp.strftime('%y%m%d_%H%M%S')
file_log = open(fname_log + '.log', 'w')

file_log.write('###############################################################################\n')
file_log.write('Initial measurement time: ' + 'some time...\n')
file_log.write('Initial (x, y): (%.4f, %.4f) \n' %(x_track[-1][0], x_track[-1][1]))
file_log.write('Initial figure of merit: %.3f \n' %f_track[-1])
file_log.write('\n')

###############################################################################
# Convergence criteria
# Criteria 1: if the change in x is less than some % of min(x_length, y_length) -> STOP!
# Criteria 2: if the change is f is less than some % of max(FOM) -> STOP!
# Criteria 3: if the next step size is less than some % of min(x_length, y_length) -> STOP!

# if the step size or difference in x is less than 5% of the max dimension of
# of the problem, we stop
epsilon1 = 0.001
# if the difference in f is less than 3% of the max FOM, STOP
epsilon2 = 2*pow(0.384,2) * 0.01 #


###############################################################################
# Gradient descent iteration

while True:
    try:
        outputs = gd_iteration(f_FOM, x_track, f_track, grad_track, grad_norm_track, alpha_track, i, limits, epsilon1, m, file_log, Read_Steps, Threshold_Percent)
        
        # unpack variables and update lists
        x_inside, x_boundary, x_armijo, x, f, grad, grad_norm, alpha, m = outputs; del outputs
        x_track.append(x)
        f_track.append(f)
        grad_track.append(grad)
        grad_norm_track.append(grad_norm)
        if i > 1: # initial alpha already included into list
            alpha_track.append(alpha)
                # update plot
        update_plot(ax11, x_boundary, x_inside, x_armijo, x, i)
        
        # Convergence checks
        x_diff, convergence = converge_v1(x_track, epsilon1) # check criteria 1
        if convergence == True:
            # Update file with convergence criteria
            file_log.write('\n')
            file_log.write('Convergence criteria 1 met')
            break
        f_diff, convergence = converge_v2(f_track, epsilon2) # check criteria 2
        if convergence == True:
            # Update file with convergence criteria
            file_log.write('\n')
            file_log.write('Convergence criteria 2 met')
            break
        
    except TypeError: # when convergence criteria 3 is met
        print('Convergence criteria 3 met')
        # Update file with convergence criteria
        file_log.write('\n')
        file_log.write('Convergence criteria 3 met')
        break
    
    # Update iteration counter
    i += 1
    
    # User input to continue execution
    #input('Press Enter to continue...')
        
# Close .log file
file_log.close()

###############################################################################
# Final plot to show path taken

fig22 = plt.figure(figsize=(14,9))
ax22 = fig22.add_subplot(111)
ax22.set_aspect('equal')

final_plot(f_FOM, fig22, ax22, x_track, i, m)

input('Execution terminated. Press Enter to close...')
