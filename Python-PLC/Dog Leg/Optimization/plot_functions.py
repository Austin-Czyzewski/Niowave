import matplotlib.pyplot as plot


def plot_traj(axes, x_fit, fit_function, horz, vert, px, py):
    # This function generates plots for the trajectories of a horizontal
    # and vertical scan
    
    # Generate axes for figure handle
    ax11 = axes[0]
    ax12 = axes[1]
    
    # Trajectory plots
    ax11.plot(horz[:,0], horz[:,1], 'o', markersize=3, color='blue')
    ax11.plot(x_fit, fit_function(x_fit, *px), color='blue')
    ax11.axhline(0, color='black')
    ax11.axvline(0, color='black')
    ax11.set_title('Horizontal scan trajectory')
    ax11.set_xlabel('WF6x (A)')
    ax11.set_ylabel('WF7x (A)')
    ax11.set_aspect(aspect='equal')
    ax11.set_xlim(-0.5, 0.5)
    ax11.set_ylim(-0.5, 0.5)
    ax11.grid(b=True, axis='both')
    ax11.spines['right'].set_visible(False)
    ax11.spines['top'].set_visible(False)
    ax11.spines['left'].set_visible(False)
    ax11.spines['bottom'].set_visible(False)
    
    
    ax12.plot(vert[:,2], vert[:,3], 'o', markersize=3, color='red')
    ax12.plot(x_fit, fit_function(x_fit, *py), color='red')
    ax12.axhline(0, color='black')
    ax12.axvline(0, color='black')
    ax12.set_title('Vertical scan trajectory')
    ax12.set_xlabel('WF6y (A)')
    ax12.set_ylabel('WF7y (A)')
    ax12.set_aspect(aspect='equal')
    ax12.set_xlim(-0.8, 0.2)
    ax12.set_ylim(-0.5, 0.5)
    ax12.grid(b=True, axis='both')
    ax12.spines['right'].set_visible(False)
    ax12.spines['top'].set_visible(False)
    ax12.spines['left'].set_visible(False)
    ax12.spines['bottom'].set_visible(False)
    
    
    
def plot_scatter(fig, axes, yint_x, yint_y, fom, perturb=False):
    # This function generates a scatter plot for the figure of merit (FOM)
    # FOM = FWHMx^2 + FWHMy^2 versus the y-intercept values of the 
    # horizontal and vertical scans
    
    # Generate axes for figure handle
    ax1 = axes
    
    if perturb == False:
        # FOM vs y-intecepts plot
        a1 = ax1.scatter(yint_x, yint_y, c=fom, s=200, edgecolor='None', cmap='jet')
        ax1.set_xlabel(r'$a_x$', fontsize=14)
        ax1.set_ylabel(r'$a_y$', fontsize=14)
        ax1.set_title('FOM: ' + r'$\rho^2 = FWHM_x^2 + FWHM_y^2$',fontsize=19)
        ax1.grid(b=True, axis='both')
        cbar1 = fig.colorbar(a1, ax=ax1)
        cbar1.ax.tick_params(labelsize=16)
        ax1.tick_params(labelsize=14)
    else:
        # FOM vs y-intecepts plot
        ax1.text(yint_x[-2], yint_y[-2], 'X', fontsize=13, fontweight='bold', color='magenta',
         horizontalalignment='center', verticalalignment='center')
        ax1.text(yint_x[-1], yint_y[-1], 'X', fontsize=13, fontweight='bold',color='darkgoldenrod',
          horizontalalignment='center', verticalalignment='center')
        
def linear_fit(x,a,b):
    return a + b*x

        