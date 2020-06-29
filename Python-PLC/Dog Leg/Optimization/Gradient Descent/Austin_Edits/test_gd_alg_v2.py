import numpy as np
import matplotlib.pyplot as plt
import random
from gd_functions import init_plot, update_plot, final_plot, gd_iteration, converge_v1
import Tag_Database as Tags
import Dog_Leg_Master as M


def f_FOM(x,y):
    D = 20
    L = 1000
    return -(2*pow(D,2) - 2*D*L*(np.abs(x) + np.abs(y)) + pow(L,2)*(x*x + y*y))

###############################################################################
# Initialize figures

fig1 = plt.figure(figsize=(14,9))
ax1 = fig1.add_subplot(111)
ax1.set_aspect('equal')

fig2 = plt.figure(figsize=(14,9))
ax2 = fig2.add_subplot(111)
ax2.set_aspect('equal')

###############################################################################
# Initialize
xmin, xmax, ymin, ymax = -0.019, 0.019, -0.019, 0.019
limits = (xmin, xmax, ymin, ymax)
alpha = 1e-6

Client = M.Make_Client('10.50.0.10')

Tag_List = [[WF6H_Tag, False], [WF7H_Tag, False], [WF6V_Tag, False], [WF7V_Tag, False], \
                [Tags.Emitted_Current, True], [Tags.Recirculator_Halfway, True], \
                [Tags.Recirculator_Bypass, True], [Tags.CU_V, False], [Tags.SRF_Pt, False]]

Pulsing_Status = bool(M.Read(Client, Tags.Pulsing_Output, Bool = True)) #Detects whether pulsing or not

if Pulsing_Status:
    count = 25 #Integer. How many points will be recorded at each step and averaged over if pulsing
    sleep_time = 0.010 #Float.(S)
else:
    count = 10 #Non-pulsing count of avg
    sleep_time = 0.010 #Non-pulsing sleep

# random guess for x_0
#x = np.array([random.uniform(-0.013, 0.013), random.uniform(-0.013, 0.013)])
x = np.array([M.Read(Client, Tags.WF6H), M.Read(Client, Tags.WF6V)])
print('initial x_0 = [%.3f, %.3f]' %(x[0], x[1]))

# f(x_0)
#f = f_FOM(x[0], x[1])

f = M.Dog_Leg(Client, Tags.WF6H, Tags.WF7H, Tags.WF6V, Tags.WF7V, \
              Tags.Recirculator_Bypass, Tags.Recirculator_Halfway, \
              Tag_List, \
              x[0], M.Read(Client, Tags.WF7H), \
              x[1], M.Read(Client, Tags.WF7V), \
              count = count, sleep_time = sleep_time, \
              Threshold_Percent = 0, Read_Steps = 40)

print('f(x_0) = %.5f' %f)

# Draw initial point on plot
init_plot(f_FOM, fig1, ax1, limits, x)

# Iteration counter
i = 1

# Measurement counter
m = 1 # start with at least 1 dog leg measurement 


########################################
# For each iteration track:
    # x_k
    # f(x_k)
    # grad(x_k)
    # p(x_k)
    # direction associated with p(x_k)
    # alpha_k
#######################################
x_track = [x]
f_track = [f]
grad_track = []
alpha_track = [alpha]

# Clean up variables
del x, f, alpha


###############################################################################
# Convergence criteria
# Criteria 1: if the change in x is less than some % of min(x_length, y_length) -> STOP!
# Criteria 2: if the next step size is less than some % of min(x_length, y_length) -> STOP!

# if the step size or difference in x is less than 5% of the max dimension of
# of the problem, we stop
epsilon = 0.05 *min(xmax-xmin, ymax-ymin)



###############################################################################
# Gradient descent iteration

while True:
    try:
        outputs = gd_iteration(f_FOM, x_track, f_track, grad_track, alpha_track, i, limits, epsilon, m)
        
        # unpack variables and update lists
        x_inside, x_boundary, x_armijo, x, f, grad, alpha, m = outputs; del outputs
        x_track.append(x)
        f_track.append(f)
        grad_track.append(grad)
        alpha_track.append(alpha)
        
        # update plot
        update_plot(ax1, x_boundary, x_inside, x_armijo, x, i)
        
        # Convergence check
        x_diff, convergence = converge_v1(x_track, epsilon, limits) # check criteria 1
        if convergence == True:
            break
        
    except TypeError: # when convergence criteria 2 is met
        print('Convergence criteria 2 met')
        break
    
    # Update iteration counter
    i += 1
        

###############################################################################
# Final plot to show path taken

final_plot(f_FOM, fig2, ax2, x_track, limits, i, m)


