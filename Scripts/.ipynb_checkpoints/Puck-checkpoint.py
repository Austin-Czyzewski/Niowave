# This is not complete, and barely works. It was quickly killed here lie the remains.

import Master as M
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d, Axes3D
from datetime import datetime

class puck:
    
    WFH_Location = 0
    WFV_Location = 0
    
    Averaging_Number = 10
    
    Step_Size = .5
    max_grid = 7000
    
    Data = np.array([["X","Y","Z"]])
    
    def take_data(self):
        
        temp_list = []
        for i in range(self.Averaging_Number):
            temp_list.append(np.random.random())
                
        self.Data = np.append(self.Data,[[round(self.WFH_Location,3), round(self.WFV_Location,3), round(sum(temp_list)/self.Averaging_Number,3)]], axis = 0)
        
        return
    
    def walk_horizontal(self, distance, step_size = None):
        if step_size is None:
            step_size = self.Step_Size
            
        if step_size > abs(distance):
            while step_size >= abs(distance):
                step_size = step_size / 3
            print("Step size too large; cut to {0:.3f}".format(step_size))
        
        start_location = self.WFH_Location
        end_location = self.WFH_Location + distance
        
        for i in range(self.max_grid):
            
            if abs(end_location - self.WFH_Location) <= step_size:
                
                self.WFH_Location = end_location
                self.take_data()
                break
                
            else:
                if distance < 0:
                    self.WFH_Location -= step_size
                    self.take_data()
                else:
                    self.WFH_Location += step_size
                    self.take_data()
        return
    
    def walk_vertical(self, distance, step_size = None):
        if step_size is None:
            step_size = self.Step_Size
            
        if step_size > abs(distance):
            while step_size > abs(distance):
                step_size = step_size / 3
            print("Step size too large; cut to {0:.3f}".format(step_size))
        
        start_location = self.WFV_Location
        end_location = self.WFV_Location + distance
        
        for i in range(self.max_grid):
            
            if abs(end_location - self.WFV_Location) <= step_size:
                
                self.WFV_Location = end_location
                self.take_data()
                break
                
            else:
                if distance < 0:
                    self.WFV_Location -= step_size
                    self.take_data()
                else:
                    self.WFV_Location += step_size
                    self.take_data()
        return
            
            
            
    def walk_to(self, Horizontal, Vertical,step_size = None, chunks = 10):
        
        if step_size is None:
            step_size = self.Step_Size
        
        for i in range(chunks):
            self.walk_horizontal(Horizontal/chunks);
            self.walk_vertical(Vertical/chunks);
                
            
    def Plot(self, save = False):
        
        x = self.Data[1:,0]
        x = x.astype(np.float)

        y = self.Data[1:,1]
        y = y.astype(np.float)

        z = self.Data[1:,2]
        z = z.astype(np.float)
        
        fig = plt.figure(figsize = (12,8))
        
        ax = Axes3D(fig)
        ax.scatter(x, y, z, c=z, cmap='viridis', linewidth=0.5)

        ax.set_xlabel("Window Frame Horizontal Amperage")
        ax.set_ylabel("Window Frame Vertical Amperage")
        ax.set_zlabel("Collected Current")
        ax.set_title("Gathered Data")
        
        if save != False:
            if save == True:
                now = datetime.today().strftime('%y%m%d_%H%M')
                plt.savefig(now + '_graph' + '.svg')
            else:
                plt.savefig(save + '.svg')
    
    def save_data(self):
        now = datetime.today().strftime('%y%m%d_%H%M') #Taking the current time in YYMMDD_HHmm format to save the plot and the txt file

        with open(now +'.txt', 'w') as f: #Open a new file by writing to it named the date as created above + .txt
    
            for i in Total_Data:
                f.write(str(i) + '\n')
        
            f.close()
        

            
    
puck = puck()
print(puck.WFH_Location)
puck.walk_to(0.1, 3)
puck.Plot()
