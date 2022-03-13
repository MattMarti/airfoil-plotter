import re
import argparse

from airfoil_defs.naca_four_digit_airfoil import NacaFourDigitAirfoil


def get_parser():
    parser = argparse.ArgumentParser(description="Export airfoil surface points to a file")
    parser.add_argument("digits", type=str, help="NACA airfoil digits")
    parser.add_argument("file", type=str, help="File to print surface points to")
    parser.add_argument("--count", type=int, default=200, help="Number of points in export file")
    return parser


def main():
    args = get_parser().parse_args()
    

if __name__ == "__main__":
    main()
