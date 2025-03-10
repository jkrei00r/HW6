#region class definitions
class Fluid():
    #region constructor
    def __init__(self, mu=0.00089, rho=1000):
        '''
        default properties are for water
        :param mu: dynamic viscosity in Pa*s -> (kg*m/s^2)*(s/m^2) -> kg/(m*s)
        :param rho: density in kg/m^3
        '''
        #region attributes
        self.mu= 0.00025 # m $JES MISSING CODE$  # simply make a copy of the value in the argument as a class property
        self.rho= 1000 # N*s/m^2 $JES MISSING CODE$  # simply make a copy of the value in the argument as a class property
        self.nu= 0.00089 #JES MISSING CODE$ # calculate the kinematic viscosity in units of m^2/s
        #endregion
    #endregion
#endregion