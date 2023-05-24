import argparse
import sys

import lib.figures as figures

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='MSMO Plotter', description='Generate figures to visualize the MSMO dataset')
    parser.add_argument('plots', metavar='P', type=str, nargs='+',
                    help='Plots to generate and save')
    parser.add_argument('-o', '--output-path', help='Output file for generated plot')
    return parser


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args(sys.argv[1:])

    for plot in args.plots:
        fig = eval(f"figures.{plot}()")
        if args.output_path:
            fig.savefig(args.output_path, dpi=500)