import numpy as np
import matplotlib.pyplot as plt
import seaborn
import time
seaborn.set()


def function(x_cord, y_cord):
    return 0.5 * x_cord**2 - 4 * x_cord + 0.2 * y_cord**2 + 2.7 * y_cord + 17.8

def centroid(vertex1, vertex2, vertex3):
    '''Vertices in the format:
    vertex1 = [X,Y]
    vertex2 = [X,Y]
    vertex3 = [X,Y]
    '''
    Ox = (vertex1[0] + vertex2[0] + vertex3[0])/3
    Oy = (vertex1[1] + vertex2[1] + vertex3[1])/3
    plt.scatter(Ox, Oy, color = 'black', label = 'centroid')
    return np.array([Ox, Oy])


def reflection_coordinate(worst_vertex, centroid, alpha = 1):
    '''blah
    
    '''    
    Xr = centroid + alpha*(centroid - worst_vertex)
    plt.scatter(Xr[0], Xr[1], color = 'blue', label = 'reflected coordinate', alpha = 0.25)
    return Xr

def expansion_coordinate(reflected_coordinate, centroid, gamma = 2):
    Xe = centroid + gamma*(reflected_coordinate - centroid)
    plt.scatter(Xe[0], Xe[1], color = 'gray', label = 'expansion coordinate', alpha = 0.25)
    return Xe

def contraction_coordinate(worst_vertex, centroid, rho = 0.5):
    Xc = centroid + rho*(worst_vertex - centroid)
    plt.scatter(Xc[0], Xc[1], color = 'firebrick', label = 'contraction coordinate', alpha = 0.25)
    return Xc

def simplex_optimization_step(dog_legs, alpha = 1, gamma = 2, rho = 0.5):
    """Dog Legs in the format:
        [[WFH, WFV, FOM],
         [WFH, WFV, FOM],
         [WFH, WFV, FOM]]
    
    """
    
    v1 = dog_legs[0]
    v2 = dog_legs[1]
    v3 = dog_legs[2]
    
    plt.scatter(dog_legs[:,0], dog_legs[:,1], color = 'red')
    
    Xo = centroid(v1[:2], v2[:2], v3[:2])
    
    worst_index = np.where(dog_legs[:,2] == min(dog_legs[:,2]))[0][0]
    best_index = np.where(dog_legs[:,2] == max(dog_legs[:,2]))[0][0]
    middle_index = np.where([i not in [best_index,worst_index] for i in [0,1,2]])[0][0] #Getting the index not used in [0,1,2]
        
    Xr = reflection_coordinate(dog_legs[worst_index,:2], Xo)
    #Xe = expansion_coordinate(Xr, Xo)
    #Xc = contraction_coordinate(dog_legs[worst_index,:2], Xo)
    
    #print(Xr, Xe, Xc)
    
    ##############
    #Ramp_Two to Xr, perform a dog leg
    #perform dog leg at Xr, get the figure of merit and compare in the following way
    ##############
    
    reflected_FOM = function(Xr[0], Xr[1]) #fake dog leg results
    

    if reflected_FOM > dog_legs[middle_index,2] and reflected_FOM <= dog_legs[best_index,2]:
        #replace worst coordinates with Xr and end of simplex step
        print('reflection step')
        reflected_coords = list(Xr)
        reflected_coords.append(reflected_FOM)
        dog_legs[worst_index] = np.array(reflected_coords)
        return dog_legs
    
    if reflected_FOM > max(dog_legs[:,2]):
        # Run a dog leg at Xe
        #Ramp_Two
        print('expansion step')
        Xe = expansion_coordinate(Xr, Xo)
        expansion_FOM = function(Xe[0], Xe[1])
        if expansion_FOM > reflected_FOM:
            expansion_coords = list(Xe)
            expansion_coords.append(expansion_FOM)
            dog_legs[worst_index] = np.array(expansion_coords)
            return dog_legs
        else:
            reflected_coords = list(Xr)
            reflected_coords.append(reflected_FOM)
            dog_legs[worst_index] = np.array(reflected_coords)
            return dog_legs
            
    
    if reflected_FOM <= dog_legs[middle_index,2]:
        # Run a dog leg at Xc
        #Ramp_Two
        print('ccontraction step')
        Xc = contraction_coordinate(dog_legs[worst_index,:2], Xo)
        contraction_FOM = function(Xc[0], Xc[1])
        if contraction_FOM >= dog_legs[worst_index,2]:
            contraction_coords = list(Xc)
            contraction_coords.append(contraction_FOM)
            dog_legs[worst_index] = np.array(contraction_coords)
            return dog_legs
        else:
            print("Your function is too far from the maximum please choose a new set of starting points")
    else:
        print("You gotta be kidding me")
        print(reflected_FOM)
        
sample_data = [[1,0],
              [.3,.2],
              [.5,-.3]]

sample_data[0].append(function(sample_data[0][0], sample_data[0][1]))
sample_data[1].append(function(sample_data[1][0], sample_data[1][1]))
sample_data[2].append(function(sample_data[2][0], sample_data[2][1]))

sample_data = np.array(sample_data)

plt.figure(figsize = (12,8))
plt.show()
new_simplex = simplex_optimization_step(sample_data)
for _ in range(10):
    new_simplex = simplex_optimization_step(new_simplex)
    time.sleep(1)
    plt.draw()
#plt.legend();
print(new_simplex, 'aaaa')
#plt.plot(new_simplex[:,0], new_simplex[:,1], alpha = 0.25, linewidth = 10)