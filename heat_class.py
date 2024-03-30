import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.animation import FuncAnimation
import sys
import time
import termios
import tty

class HeatEquation:
    def __init__(self):
        self.params = {}

        #graph settings
        #
        #set amount of pixels on each side
        self.params['width'] = [102, '1', 'mm']
        self.params['height'] = [102, '2', 'mm']

        #surrounding
        #
        #temp set of heat bath
        self.params['boundary'] = [200, '3', 'Kelvin']
        #initial heat of surroundings
        self.params['i_heat'] = [0, '4', 'Kelvin']
        #set thermal diffusivity of surroundings
        self.params['s_diff'] = [80, '5', 'mm^2/s']

        #object
        #
        #initial heat of object
        self.params['obj_heat'] = [200, '6', 'Kelvin']
        #thermal diffusivity of object
        self.params['obj_diff'] = [10, '7', 'mm^2/s']
        #x and y position of the box
        self.params['xpos'] = [50, '8', 'mm']
        self.params['ypos'] = [50, '9', 'mm']
        #width and height of box
        self.params['bwidth'] = [20, '10', 'mm']
        self.params['bheight'] = [20, '11', 'mm']

        self.iteration = 0

        self.paramkeys = {}
        for i in self.params.keys():
            self.paramkeys[self.params[i][1]] = i

    def create_conditions(self):
        #print(self.params)
        # Create numpy arrays and populate with values of

        self.width = self.params['width'][0]
        self.height = self.params['height'][0]
        self.boundary = self.params['boundary'][0]
        self.i_heat = self.params['i_heat'][0]
        self.s_diff = self.params['s_diff'][0]
        self.obj_heat = self.params['obj_heat'][0]
        self.obj_diff = self.params['obj_diff'][0]
        self.xpos = self.params['xpos'][0]
        self.ypos = self.params['ypos'][0]
        self.bwidth = self.params['bwidth'][0]
        self.bheight = self.params['bheight'][0]

        self.u = np.full((self.width,self.height),self.i_heat)

        self.alpha = np.full((self.width,self.height),self.s_diff)

        if self.s_diff > self.obj_diff:
            self.constant = 1/(16*self.s_diff)
        else:
            self.constant = 1/(16*self.obj_diff)

        # setting the temp of the boundary
        self.u[(0,self.width-1),:] = self.boundary
        self.u[:,(0,self.height-1)] = self.boundary

        #setting the temp of object


        x1 = round(self.xpos-self.bwidth/2)
        x2 = round(self.xpos+self.bwidth/2)
        y1 = round(self.ypos-self.bheight/2)
        y2 = round(self.ypos+self.bheight/2)
        self.u[x1:x2,y1:y2] = self.obj_heat
        self.alpha[x1:x2,y1:y2] = self.obj_diff

        plotarr = np.flipud(self.u.T)
        self.fig, self.ax = plt.subplots()
        #self.ax.add_patch(plt.Polygon([(x1,y1),(x2,y1),(x2,y2),(x1,y2)]))
        self.text = self.ax.text(1,1,"iteration = %s" % self.iteration)
        self.picture = self.ax.imshow(plotarr, interpolation='none', cmap='jet', animated=True)

        self.a_y = np.roll(self.alpha, 1, axis=0)-np.roll(self.alpha, -1, axis=0)
        self.a_x = np.roll(self.alpha, 1, axis=1)-np.roll(self.alpha, -1, axis=1)

    def print_menu(self):
        """Print current parameter values and menu.
        """
        paramlist = ['width', 
        'height', 
        '',
        'boundary',
        'i_heat',
        's_diff',
        '',
        'obj_heat',
        'obj_diff',
        'xpos',
        'ypos',
        'bwidth',
        'bheight']
        namewidth = max(map(len,paramlist))
        print('Set Params')
        print('~~~~~~~~~~~~~~~~~~~')
        print
        for i in paramlist:
            if i == '':
                print('~~~~~~~~~~')
            else:
                print(self.params[i][1])
                spaces = namewidth - len(i)
                ival = self.params[i][0]
                print(i + ': ' + str(ival) + ' ' + self.params[i][2])
                print()
                
    
    def cls(self):
        """Clear screen.
        """
        CLS = '\x1b[H\x1b[2J'
        sys.stdout.write(CLS)
        sys.stdout.flush()

    def menu_loop(self):
        """Print parameter menu and enter command loop.
        """
        self.cls()
        sys.stdout.flush()
        while True:
            self.cls()
            self.print_menu() 

            print
            print
            print ("Select a parameter by number ('c' to continue to animation): ",)
            ch = str(input())
    
            if ch == 'c':
                print
                print
                return

            if ch == ' ':
                continue

   
            try:
                pname = self.paramkeys[ch]
            except KeyError:
                continue

            print
            print
            print
            print ('Enter new value for %s: ' % pname,)
         
            instring = sys.stdin.readline().strip()
            insplit = instring.split()
            print

            try:
                inval = int(insplit[0])
            except:
                sys.stderr.write('%s: invalid input ' % instring)
                time.sleep(2)
                continue

            unit = self.params[pname][2]
            uflag = False

            if len(insplit) > 1:
                uflag = True
                try:
                    unitindex = self.params[pname].index(insplit[1])
                except ValueError:
                    sys.stderr.write('%s: unsupported unit for %s ' %
                        (insplit[1], pname))
                    time.sleep(2)
                    continue

            if uflag:
                unit = insplit[1]
                conv = self.params[pname][unitindex-2]

            if inval < 0:
                sys.stderr.write('%.2f %s: invalid %s '
                % (inval, unit, pname))
                time.sleep(2)
                continue

            self.params[pname][0] = inval

            self.cls()
        
    def func(self, data):
        u = data
        a = self.constant*(self.a_x*(np.roll(u, 1, axis=1) - np.roll(u, -1, axis=1)) + self.a_y*(np.roll(u, 1, axis=0) - np.roll(u, -1, axis=0)))/4
        b = self.constant*self.alpha*(np.roll(u,-1,axis=0) + np.roll(u,1,axis=0) + np.roll(u,-1,axis=1) + np.roll(u,1,axis=1) -4*u)
        u = a + b + u
        u[(0,self.width-1),:] = self.boundary
        u[:,(0,self.height-1)] = self.boundary
        return u
    
    def update(self, data):
        self.u = self.func(self.u)
        plotarr = np.flipud(self.u.T)
        self.picture.set_array(plotarr)
        self.iteration += 1
        self.text.set_text("Iteration: %s" % self.iteration)
        return self.picture,

if __name__ == '__main__':
    #check_arguments()

    he = HeatEquation()
    he.menu_loop()
    he.create_conditions()
    print(he.bheight)
    ani = animation.FuncAnimation(he.fig, he.update,  blit=True)
    he.fig.show()
    input("\nPress <Enter> to stop animation...\n")