# region imports
import numpy as np
from scipy.interpolate import griddata


# endregion

# region class definitions
class steam():
    """
    The steam class is used to find thermodynamic properties of steam along an isobar.
    The Gibbs phase rule tells us we need two independent properties in order to find
    all the other thermodynamic properties. Hence, the constructor requires pressure of
    the isobar and one other property.
    """

    def __init__(self, pressure, T=None, x=None, v=None, h=None, s=None, name=None):
        '''
        Constructor for steam
        :param pressure: pressure in kPa
        :param T: Temperature in degrees C
        :param x: quality of steam x=1 is saturated vapor, x=0 is saturated liquid
        :param v: specific volume in m^3/kg
        :param h: specific enthalpy in kJ/kg
        :param s: specific entropy in kJ/(kg*K)
        :param name: a convenient identifier
        '''
        # Assign arguments to class properties
        self.p = pressure  # Pressure - kPa
        self.T = T  # Temperature - degrees C
        self.x = x  # Quality
        self.v = v  # Specific volume - m^3/kg
        self.h = h  # Specific enthalpy - kJ/kg
        self.s = s  # Entropy - kJ/(kg*K)
        self.name = name  # A useful identifier
        self.region = None  # 'superheated' or 'saturated' or 'two-phase'

        if T is None and x is None and v is None and h is None and s is None:
            return
        else:
            self.calc()

    def calc(self):
        '''
        The Rankine cycle operates between two isobars (i.e., p_high (Turbine inlet state 1) & p_low (Turbine exit state 2)
        So, given a pressure, we need to determine if the other given property puts
        us in the saturated or superheated region.
        :return: nothing returned, just set the properties
        '''
        # Read in the thermodynamic data from files, skipping the first row (titles)
        ts, ps, hfs, hgs, sfs, sgs, vfs, vgs = np.loadtxt('sat_water_table.txt', unpack=True,
                                                          skiprows=1)  # Saturated properties
        tcol, hcol, scol, pcol = np.loadtxt('superheated_water_table.txt', unpack=True,
                                            skiprows=1)  # Superheated properties

        R = 8.314 / (18 / 1000)  # Ideal gas constant for water [J/(mol K)]/[kg/mol]
        Pbar = self.p / 100  # Pressure in bar - 1 bar = 100 kPa roughly

        # Get saturated properties
        Tsat = float(griddata((ps), ts, (Pbar)))  # Saturation temperature at P
        hf = float(griddata((ps), hfs, (Pbar)))  # Enthalpy of saturated liquid
        hg = float(griddata((ps), hgs, (Pbar)))  # Enthalpy of saturated vapor
        sf = float(griddata((ps), sfs, (Pbar)))  # Entropy of saturated liquid
        sg = float(griddata((ps), sgs, (Pbar)))  # Entropy of saturated vapor
        vf = float(griddata((ps), vfs, (Pbar)))  # Specific volume of saturated liquid
        vg = float(griddata((ps), vgs, (Pbar)))  # Specific volume of saturated vapor

        self.hf = hf  # Saturated liquid enthalpy as a class member variable

        # Region determination based on the known property
        if self.T is not None:
            if self.T > Tsat:  # Superheated steam
                self.region = 'Superheated'
                self.h = float(griddata((tcol, pcol), hcol, (self.T, Pbar)))  # Superheated enthalpy
                self.s = float(griddata((tcol, pcol), scol, (self.T, Pbar)))  # Superheated entropy
                self.x = 1.0  # For superheated steam, x = 1
                TK = self.T + 273.14  # Temperature conversion to Kelvin
                self.v = R * TK / (self.p * 1000)  # Ideal gas approximation for specific volume
            else:  # Saturated steam
                self.region = 'Saturated'
                self.x = (self.h - hf) / (hg - hf)  # Calculate quality (x) for saturated steam
                self.x = max(0.0, min(self.x, 1.0))  # Ensure quality is between 0 and 1
                self.T = Tsat  # Saturation temperature
                self.h = hf + self.x * (hg - hf)  # Calculate enthalpy
                self.s = sf + self.x * (sg - sf)  # Calculate entropy
                self.v = vf + self.x * (vg - vf)  # Calculate specific volume
        elif self.x is not None:  # If quality (x) is known
            self.region = 'Saturated'
            self.T = Tsat  # Saturation temperature
            self.h = hf + self.x * (hg - hf)  # Calculate enthalpy
            self.s = sf + self.x * (sg - sf)  # Calculate entropy
            self.v = vf + self.x * (vg - vf)  # Calculate specific volume
        elif self.h is not None:  # If enthalpy (h) is known
            self.x = (self.h - hf) / (hg - hf)  # Calculate quality (x)
            self.x = max(0.0, min(self.x, 1.0))  # Ensure quality is between 0 and 1
            if self.x <= 1.0:  # Saturated steam
                self.region = 'Saturated'
                self.T = Tsat
                self.s = sf + self.x * (sg - sf)
                self.v = vf + self.x * (vg - vf)
            else:  # Superheated steam
                self.region = 'Superheated'
                self.T = float(griddata((pcol, hcol), tcol, (Pbar, self.h), method='linear'))
                self.s = float(griddata((pcol, hcol), scol, (Pbar, self.h), method='linear'))
        elif self.s is not None:  # If entropy (s) is known
            self.x = (self.s - sf) / (sg - sf)  # Calculate quality (x)
            self.x = max(0.0, min(self.x, 1.0))  # Ensure quality is between 0 and 1
            if self.x <= 1.0:  # Saturated steam
                self.region = 'Saturated'
                self.T = Tsat
                self.h = hf + self.x * (hg - hf)
                self.v = vf + self.x * (vg - vf)
            else:  # Superheated steam
                self.region = 'Superheated'
                self.T = float(griddata((pcol, scol), tcol, (Pbar, self.s), method='linear'))
                self.h = float(griddata((pcol, scol), hcol, (Pbar, self.s), method='linear'))

    def print(self):
        """
        This prints a nicely formatted report of the steam properties.
        :return: nothing, just prints to screen
        """
        print('Name: ', self.name)
        if self.x < 0.0:
            print('Region: compressed liquid')
        else:
            print('Region: ', self.region)
        print('p = {:0.2f} kPa'.format(self.p))
        if self.x >= 0.0:
            print('T = {:0.1f} degrees C'.format(self.T))
        print('h = {:0.2f} kJ/kg'.format(self.h))
        if self.x >= 0.0:
            print('s = {:0.4f} kJ/(kg K)'.format(self.s))
            if self.region == 'Saturated':
                print('v = {:0.6f} m^3/kg'.format(self.v))
            if self.region == 'Saturated':
                print('x = {:0.4f}'.format(self.x))
        print()


# endregion

# region function definitions
def main():
    inlet = steam(7350, name='Turbine Inlet')  # Not enough information to calculate
    inlet.x = 0.9  # 90 percent quality
    inlet.calc()
    inlet.print()

    h1 = inlet.h
    s1 = inlet.s
    print(h1, s1, '\n')

    outlet = steam(100, s=inlet.s, name='Turbine Exit')
    outlet.print()

    another = steam(8575, h=2050, name='State 3')
    another.print()
    yetanother = steam(8575, h=3125, name='State 4')
    yetanother.print()


# endregion

# region function calls
if __name__ == "__main__":
    main()
# endregion
