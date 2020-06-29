import numpy as np
import matplotlib.pyplot as plt
import Tag_Database as Tags
import Dog_Leg_Master as M

###############################################################################
# Plotting functions

def init_plot(f, fig1, ax1, limits, x0):
    
    xmin, xmax, ymin, ymax = limits
    x = np.linspace(xmin, xmax, 1000)
    y = np.linspace(ymin, ymax, 1000)
    
    ###########################################################################
    # Plot
    
    ## Generate meshgrid
    xx, yy = np.meshgrid(x,y)
    fxy =f(xx,yy)
    
    a1 = ax1.pcolormesh(xx, yy, fxy)
    cbar1 = fig1.colorbar(a1, ax=ax1)
    cbar1.ax.tick_params(labelsize=20)
    
    # Contour plot
    cnt_f_FOM = [-800, -750, -700, -650, -600, -550, -500, -450, -400, -350,
                 -300, -250, -200, -150, -100, -50, 0]
    contours = ax1.contour(xx, yy, fxy, cnt_f_FOM, 
                           linewidths=1, cmap='gist_yarg')
    ax1.clabel(contours, inline=True, use_clabeltext=True, fontsize=20)
    
    # labels to fig
    ax1.set_xlabel('x', fontsize=20)
    ax1.set_ylabel('y', fontsize=20)
    ax1.grid(b=True, axis='both')
    ax1.tick_params(labelsize=16)
    ax1.set_xlim(xmin, xmax)
    ax1.set_ylim(ymin, ymax)
    
    # Draw initial point on plot
    ax1.scatter(x0[0], x0[1], color='red', s=100)
    ax1.text(x0[0], x0[1]-0.002, str(0), fontsize=20, fontweight='bold', color='red',
             horizontalalignment='center', verticalalignment='center')

    # Title
    ax1.set_title(r'''All measurements needed. Blue: outside boundary,
              magenta: $f(x_{k+_1}) > f(x_k)$, green: good points''', fontsize=20)

def update_plot(ax1, x_boundary, x_inside, x_armijo, x, i):

    # Plot the guess points that lie outside the boundary
    if len(x_boundary) > 1:
        x_boundary = np.array(x_boundary)
        ax1.plot(x_boundary[:,0], x_boundary[:,1], ':o', ms=10, color='deepskyblue', zorder=1)

    # Plot first guess point that lies inside the problem boundary
    ax1.scatter(x_inside[0], x_inside[1], s=100, color='black', zorder=2)

    # Plot the guess points that do not satisfy the Armijo condition
    if len(x_armijo) > 1:
        x_armijo = np.array(x_armijo)
        ax1.plot(x_armijo[:,0], x_armijo[:,1], ':x', ms=10, color='magenta', zorder=1)

    # Plot x_{k+1}
    ax1.scatter(x[0], x[1], s=100, color='green', zorder=2)

    # label the point
    ax1.text(x[0], x[1]-0.002, str(i), fontsize=20, fontweight='bold', color='green',
             horizontalalignment='center', verticalalignment='center')



def final_plot(f, fig2, ax2, x_track, limits, i, m):
    
    xmin, xmax, ymin, ymax = limits
    x = np.linspace(xmin, xmax, 1000)
    y = np.linspace(ymin, ymax, 1000)
    
    ###########################################################################
    # Plot
    
    ## Generate meshgrid
    xx, yy = np.meshgrid(x,y)
    fxy =f(xx,yy)
    
    a2 = ax2.pcolormesh(xx, yy, fxy)
    cbar2 = fig2.colorbar(a2, ax=ax2)
    cbar2.ax.tick_params(labelsize=20)
    
    # Contour plot
    cnt_f_FOM = [-800, -750, -700, -650, -600, -550, -500, -450, -400, -350,
                 -300, -250, -200, -150, -100, -50, 0]
    contours = ax2.contour(xx, yy, fxy, cnt_f_FOM, 
                           linewidths=1, cmap='gist_yarg')
    ax2.clabel(contours, inline=True, use_clabeltext=True, fontsize=20)
    
    # labels to fig
    ax2.set_xlabel('x', fontsize=20)
    ax2.set_ylabel('y', fontsize=20)
    ax2.grid(b=True, axis='both')
    ax2.tick_params(labelsize=16)
    ax2.set_xlim(xmin, xmax)
    ax2.set_ylim(ymin, ymax)

    # Draw final path taken
    x_track = np.array(x_track)
    ax2.plot(x_track[0,0], x_track[0,1], '-o', ms=10, color='red', zorder=2) # initial point
    ax2.text(x_track[0,0], x_track[0,1]-0.002, str(0), fontsize=20, fontweight='bold', color='red',
             horizontalalignment='center', verticalalignment='center', zorder=1)
    ax2.plot(x_track[:,0], x_track[:,1], '-o', ms=10, color='green', zorder=1)
    ax2.scatter(x_track[-1,0], x_track[-1,1], s=100, color='goldenrod', zorder=2) # final point
    ax2.text(x_track[-1,0], x_track[-1,1]-0.002, str(i), fontsize=20, fontweight='bold', color='goldenrod',
             horizontalalignment='center', verticalalignment='center', zorder=1)

    # Title
    ax2.set_title('Path taken to find solution. iter. = %d, total meas. = %d' %(i, m), fontsize=20)

###############################################################################
# Gradient descent function
    
    
def gd_iteration(f_FOM, x_track, f_track, grad_track, alpha_track, i, limits, epsilon, m):
    
    #Establishing connection to the PLC
    Client = M.Make_Client('10.50.0.10')

    Pulsing_Status = bool(M.Read(Client, Tags.Pulsing_Output, Bool = True)) #Detects whether pulsing or not

    if Pulsing_Status:
        count = 25 #Integer. How many points will be recorded at each step and averaged over if pulsing
        sleep_time = 0.010 #Float.(S)
    else:
        count = 10 #Non-pulsing count of avg
        sleep_time = 0.010 #Non-pulsing sleep

    WF6H_Tag = Tags.WF6H
    WF6V_Tag = Tags.WF6V
    WF7H_Tag = Tags.WF7H
    WF7V_Tag = Tags.WF7V

    Tag_List = [[WF6H_Tag, False], [WF7H_Tag, False], [WF6V_Tag, False], [WF7V_Tag, False], \
                [Tags.Emitted_Current, True], [Tags.Recirculator_Halfway, True], \
                [Tags.Recirculator_Bypass, True], [Tags.CU_V, False], [Tags.SRF_Pt, False]]

    WF1H_Start = M.Read(Client, WF6H_Tag) #Taking the start values of all of the Window Frame values
    WF2H_Start = M.Read(Client, WF7H_Tag)
    WF1V_Start = M.Read(Client, WF6V_Tag)
    WF2V_Start = M.Read(Client, WF7V_Tag)
    
    print('\n')
    print('iteration = ' + str(i))

    # Set constant for Armijo check
    beta = 0.01 # armijo condition
    
    # Set fraction for reducing the stepsize
    frac = 0.5 # reduce by half if point outside boundary or Armijo condition not met
    
    # Set dx and dy used for finite difference stencil
    dx = 0.000005/np.sqrt(2) # distance for horizontal perturubation
    dy = 0.000005/np.sqrt(2) # distance for vertical perturbation
    
    # Set problem limits
    xmin, xmax, ymin, ymax = limits
    
    # Set values from previous iteration
    x = x_track[-1]
    f = f_track[-1]
    alpha = alpha_track[-1]
    
    ###########################################################################
    # Estimate gradient
    
    # Get stencil points
    x_h = x + np.array([dx,0])
    x_v = x + np.array([0, dy])
    
    # Evaluate function at the stencil points
    ###########################################################################
    ###########################################################################
    ###########################################################################
    ###########################################################################
    #f_x = f_FOM(x[0], x[1])
    
    f_x = M.Dog_Leg(Client, WF6H_Tag, WF7H_Tag, WF6V_Tag, WF7V_Tag, \
              Tags.Recirculator_Bypass, Tags.Recirculator_Halfway, \
              Tag_List, \
              x[0], WF2H_Start, \
              x[1], WF2V_Start, \
              count = count, sleep_time = sleep_time, \
              Threshold_Percent = Threshold_Percent, Read_Steps = Read_Steps)
    
    
    #f_x_h = f_FOM(x_h[0], x_h[1])
    
    f_x_h = M.Dog_Leg(Client, WF6H_Tag, WF7H_Tag, WF6V_Tag, WF7V_Tag, \
              Tags.Recirculator_Bypass, Tags.Recirculator_Halfway, \
              Tag_List, \
              x_h[0], WF2H_Start, \
              x_h[1], WF2V_Start, \
              count = count, sleep_time = sleep_time, \
              Threshold_Percent = Threshold_Percent, Read_Steps = Read_Steps)
    
    
    #f_x_v = f_FOM(x_v[0], x_v[1])
    
    f_x_y = M.Dog_Leg(Client, WF6H_Tag, WF7H_Tag, WF6V_Tag, WF7V_Tag, \
              Tags.Recirculator_Bypass, Tags.Recirculator_Halfway, \
              Tag_List, \
              x_v[0], WF2H_Start, \
              x_v[1], WF2V_Start, \
              count = count, sleep_time = sleep_time, \
              Threshold_Percent = Threshold_Percent, Read_Steps = Read_Steps)
    ###########################################################################
    ###########################################################################
    ###########################################################################
    ###########################################################################
    m += 2 # 2 measurments to estimate gradient
    
    # Calculate derivatives
    df_dx = (f_x_h - f_x) / dx
    df_dy = (f_x_v - f_x) / dy
    
    # Assemble gradient
    grad = np.array([df_dx, df_dy])

    
    ###########################################################################
    # Calculate new step size (if not first iteration)
    if i > 1:
        alpha = alpha * np.linalg.norm(grad_track[-1]) / np.linalg.norm(grad)
    
    print('alpha = ' + str(alpha))
    print('epsilon = ' + str(epsilon))
    
    ###########################################################################
    # Step size convergence check
    # If step size is less than some amount
    # STOP!
    if np.linalg.norm(alpha * grad) <= epsilon:
        return
    
    ###########################################################################
    # Calculate new x along negative gradient direction
    x_tilde = x - alpha * grad
    
    
    ###########################################################################
    # Check to see if x_tilde is in the problem boundary
    
    if xmin < x_tilde[0] and x_tilde[0] < xmax and ymin < x_tilde[1] and x_tilde[1] < ymax:
        print('inside')
        x_boundary = [x_tilde]
        # do nothing
    else:
        print('outside')
        x_boundary = [x_tilde]
        # shrink alpha
        boundary = False
        while boundary == False:
            alpha = alpha * frac
            x_tilde = x - alpha * grad 
            x_boundary.append(x_tilde)
            if xmin < x_tilde[0] and x_tilde[0] < xmax and ymin < x_tilde[1] and x_tilde[1] < ymax:
                boundary = True
                break
    print(alpha)     
    
    x_inside = x_tilde
    
    
    ###########################################################################
    # Evaluate function at x_tilde and check Armijo condition
    
    
    ###########################################################################
    ###########################################################################
    ###########################################################################
    ###########################################################################
    #f_x_tilde = f_FOM(x_tilde[0], x_tilde[1])
    
    f_x_tilde = M.Dog_Leg(Client, WF6H_Tag, WF7H_Tag, WF6V_Tag, WF7V_Tag, \
              Tags.Recirculator_Bypass, Tags.Recirculator_Halfway, \
              Tag_List, \
              x_tilde[0], WF2H_Start, \
              x_tilde[1], WF2V_Start, \
              count = count, sleep_time = sleep_time, \
              Threshold_Percent = 0, Read_Steps = 40)
    ###########################################################################
    ###########################################################################
    ###########################################################################
    ###########################################################################
    m += 1 # measurement at the guess step
    
    if f_x_tilde < f + beta * alpha * grad.dot(-grad):
        print('Armijo yes')
        x_armijo = [x_tilde]
        # do nothing
    else:
        print('Armijo no')
        x_armijo = [x_tilde] # for direction 1
        # shrink alpha
        armijo = False
        iteration = 1
        while armijo == False:
            alpha = alpha * frac
            x_tmp = x - alpha * grad # New guess for x_tilde
            x_armijo.append(x_tmp)
            ###########################################################################
            ###########################################################################
            ###########################################################################
            ###########################################################################
            #f_x_tilde = f_FOM(x_tmp[0], x_tmp[1])
            
            f_x_tilde = M.Dog_Leg(Client, WF6H_Tag, WF7H_Tag, WF6V_Tag, WF7V_Tag, \
                      Tags.Recirculator_Bypass, Tags.Recirculator_Halfway, \
                      Tag_List, \
                      x_tmp[0], WF2H_Start, \
                      x_tmp[1], WF2V_Start, \
                      count = count, sleep_time = sleep_time, \
                      Threshold_Percent = 0, Read_Steps = 40)
            ###########################################################################
            ###########################################################################
            ###########################################################################
            ###########################################################################
            m += 1 # measurement at the new guess step
            print(alpha)
            plt.pause(1)
            iteration += 1
            if f_x_tilde < f + beta * alpha * grad.dot(-grad):
                armijo = True
                x_tilde = x_tmp
                break
            
            # Stop after a few test points
            if iteration == 5:
                x_tilde = x_tmp
                break
    
    # Set x_{k+1} and f(x_{k+1})
    x = x_tilde
    f = f_x_tilde
    
    return x_inside, x_boundary, x_armijo,\
            x, f, grad,  alpha, m
    
    
    
###############################################################################
# Convergence check functions
            
def converge_v1(x_track, epsilon, limits):
    # Check if difference in x is less than epsilon
    
    xmin, xmax, ymin, ymax = limits
    x = np.array(x_track)
    
    # Calculate the norm of the difference in successive x values
    x_diff = x[1:] - x[:-1]
    x_diff = np.linalg.norm(x_diff, axis=1)
    
    # Return convergence flag
    if x_diff[-1] <= epsilon:
        convergence = True
        print('Convergence criteria 1 met')
    else:
        convergence = False
    
    return x_diff, convergence 
    
    
    
















