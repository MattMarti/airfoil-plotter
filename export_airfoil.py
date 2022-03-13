import os
import re
import argparse

import numpy as np

from airfoil_defs.naca_four_digit_airfoil import NacaFourDigitAirfoil


def print_naca_four_digit(file:str, naca_digits:str, count:int):
    m = int(naca_digits[0])
    p = int(naca_digits[1])
    t = int(naca_digits[-2:])
    airfoil = NacaFourDigitAirfoil(m, p, t)
    
    count_u = int(np.floor(0.5 * count))
    count_l = int(np.ceil(0.5 * count))
    
    xu = np.linspace(1, 0, count_u)
    xu, yu = airfoil.get_upper(xu)
    
    xl = np.linspace(0, 1, count_l)
    xl, yl = airfoil.get_lower(xl)

    x = np.concatenate((xu, xl), axis=0)
    y = np.concatenate((yu, yl), axis=0)
    xy = np.vstack((x, y)).T

    np.savetxt(file, xy, fmt="%.12e", delimiter=", ", newline="\n")


def get_parser():
    parser = argparse.ArgumentParser(description="Export airfoil surface points to a file")
    parser.add_argument("digits", type=str, help="NACA airfoil digits")
    parser.add_argument("file", type=str, help="File to print surface points to")
    parser.add_argument("--count", type=int, default=200, help="Number of points in export file")
    parser.add_argument("-f", "--force", action="store_true", help="Force overwrite")
    return parser


def main():
    args = get_parser().parse_args()
    
    if os.path.exists(args.file) and not args.force:
        print(f"File \"{args.file}\" exists. Aborting")
        return
    
    if re.compile(r"^\d\d\d\d$").match(args.digits) is not None:
        print_naca_four_digit(args.file, args.digits, args.count)
    else:
        print(f"Unrecognized digit pattern \"{args.digits}\"")
    

if __name__ == "__main__":
    main()
