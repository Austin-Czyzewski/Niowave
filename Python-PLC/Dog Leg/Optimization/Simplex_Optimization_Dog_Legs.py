import numpy as np
import matplotlib.pyplot as plt
import seaborn
seaborn.set()

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
    plt.scatter(Xr[0], Xr[1], color = 'blue', label = 'reflected coordinate')
    return Xr

def expansion_coordinate(reflected_coordinate, centroid, gamma = 2):
    Xe = centroid + gamma*(reflected_coordinate - centroid)
    plt.scatter(Xe[0], Xe[1], color = 'gray', label = 'expansion coordinate')
    return Xe

def contraction_coordinate(worst_vertex, centroid, rho = 0.5):
    Xc = centroid + rho*(worst_vertex - centroid)
    plt.scatter(Xc[0], Xc[1], color = 'firebrick', label = 'contraction coordinate')
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
    Xe = expansion_coordinate(Xr, Xo)
    Xc = contraction_coordinate(dog_legs[worst_index,:2], Xo)
    
    print(Xr, Xe, Xc)
    
    ##############
    #Ramp_Two to Xr, perform a dog leg
    #perform dog leg at Xr, get the figure of merit and compare in the following way
    ##############
    
    reflected_FOM = .7 #fake dog leg results
    

    if reflected_FOM > dog_legs[middle_index,2] and reflected_FOM <= dog_legs[best_index,2]:
        #replace worst coordinates with Xr and end of simplex step
        reflected_coords = list(Xr)
        reflected_coords.append(reflected_FOM)
        dog_legs[worst_index] = np.array(reflected_coords)
        return dog_legs
    
    if reflected_FOM > max(dog_legs[:,2]):
        # Run a dog leg at Xe
        #Ramp_Two
        
        expansion_FOM = .65
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
            
    
    if reflected_FOM < min(dog_legs[:,2]):
        # Run a dog leg at Xc
        #Ramp_Two
    
        contraction_FOM = 0.4
        if contraction_FOM > dog_legs[worst_index,2]:
            contraction_coords = list(Xc)
            contraction_coords.append(contraction_FOM)
            dog_legs[worst_index] = np.array(contraction_coords)
            return dog_legs
        else:
            print("Your function is too far from the maximum please choose a new set of starting points")