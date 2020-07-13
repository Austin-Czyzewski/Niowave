import numpy as np
import matplotlib.pyplot as plt
import random
from gd_functions import init_plot, update_plot, final_plot, gd_iteration, converge_v1

def f_FOM(x,y):
    D = 20
    L = 1000
    return -(2*pow(D,2) - 2*D*L*(np.abs(x) + np.abs(y)) + pow(L,2)*(x*x + y*y))

###############################################################################
# Initialize figures

fig1 = plt.figure()
ax1 = fig1.add_subplot(111)

fig2 = plt.figure()
ax2 = fig2.add_subplot(111)

###############################################################################
# Initialize
xmin, xmax, ymin, ymax = -0.019, 0.019, -0.019, 0.019
limits = (xmin, xmax, ymin, ymax)
alpha = 1e-6

# random guess for x_0
x = np.array([random.uniform(-0.013, 0.013), random.uniform(-0.013, 0.013)])
print('initial x_0 = [%.3f, %.3f]' %(x[0], x[1]))

# f(x_0)
f = f_FOM(x[0], x[1])
print('f(x_0) = %.5f' %f)

# Draw initial point on plot
init_plot(f_FOM, fig1, ax1, limits, x)

# Iteration counter
i = 1

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


##########################################
# i = 1
try:
    outputs = gd_iteration(f_FOM, x_track, f_track, grad_track, alpha_track, i, limits, epsilon)
    
    # unpack variables and update lists
    x_inside, x_boundary, x_armijo, x, f, grad, alpha = outputs; del outputs
    x_track.append(x)
    f_track.append(f)
    grad_track.append(grad)
    alpha_track.append(alpha)
    
    # Convergence check
    x_diff, convergence = converge_v1(x_track, epsilon, limits) # check criteria 1
    
    # update plot
    update_plot(ax1, x_boundary, x_inside, x_armijo, x, i)
    
except TypeError: # when convergence criteria 2 is met
    print('Convergence criteria 2 met')
    





##########################################
# i = 2

# update iteration counter
i += 1

try:
    outputs = gd_iteration(f_FOM, x_track, f_track, grad_track, alpha_track, i, limits, epsilon)
    
    # unpack variables and update lists
    x_inside, x_boundary, x_armijo, x, f, grad, alpha = outputs; del outputs
    x_track.append(x)
    f_track.append(f)
    grad_track.append(grad)
    alpha_track.append(alpha)
    
    # Convergence check
    x_diff, convergence = converge_v1(x_track, epsilon, limits) # check criteria 1
    
    # update plot
    update_plot(ax1, x_boundary, x_inside, x_armijo, x, i)

except TypeError: # when convergence criteria 2 is met
    print('Convergence criteria 2 met')






##########################################
# i = 3

# update iteration counter
i += 1

try:
    outputs = gd_iteration(f_FOM, x_track, f_track, grad_track, alpha_track, i, limits, epsilon)
    
    # unpack variables and update lists
    x_inside, x_boundary, x_armijo, x, f, grad, alpha = outputs; del outputs
    x_track.append(x)
    f_track.append(f)
    grad_track.append(grad)
    alpha_track.append(alpha)
    
    # Convergence check
    x_diff, convergence = converge_v1(x_track, epsilon, limits) # check criteria 1
        
    # update plot
    update_plot(ax1, x_boundary, x_inside, x_armijo, x, i)

except TypeError: # when convergence criteria 2 is met
    print('Convergence criteria 2 met')








###############################################################################
# Final plot to show path taken

final_plot(f_FOM, fig2, ax2, x_track, limits, i)


