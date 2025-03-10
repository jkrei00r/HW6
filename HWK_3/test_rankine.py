#rankine_test.py
from rankine import rankine

def main():
    '''
    Main function to test two different Rankine cycles.
    '''
    # Rankine cycle with saturated vapor entering the turbine
    rankine1 = rankine(p_low=8, p_high=8000, t_high=None, name='Rankine Cycle (Saturated Vapor)')
    rankine1.print_summary()

    # Rankine cycle with superheated steam entering the turbine
    rankine2 = rankine(p_low=8, p_high=8000, t_high=1.7 * 295, name='Rankine Cycle (Superheated Steam)')
    rankine2.print_summary()

if __name__ == "__main__":
    main()
