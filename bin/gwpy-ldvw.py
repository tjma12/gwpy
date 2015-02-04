#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) Joseph Areeda (2015)
#
# This file is part of GWpy.
#
# GWpy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# GWpy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GWpy.  If not, see <http://www.gnu.org/licenses/>.
#
"""Command line interface to GWpy plotting functions
"""
from gwpy import version
__author__ = 'joseph areeda'
__email__ = 'joseph.areeda@ligo.org'
__version__ = version.version

VERBOSE = 3 # 0 = errors only, 1 = Warnings, 2 = INFO, >2 DEBUG >=5 ALL

import sys

if sys.version < '2.6':
    raise ImportError("Python versions older than 2.6 are not supported.")

from importlib import import_module
import argparse

#---needed to generate help messages---
class CliHelpFormatter(argparse.ArgumentDefaultsHelpFormatter):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('indent_increment', 4)
        super(CliHelpFormatter, self).__init__(*args, **kwargs)
#----

# Products are classes that implement a specific plot
# This is a list of those class names, module names
PRODUCTS = [
        'TimeSeries',
        'Coherence',
        'Spectrum',
        'Spectrogram',
        'Coherencegram'
]

parser = argparse.ArgumentParser(formatter_class=CliHelpFormatter,
                                 description=__doc__, prog='gwpy_ldvw')
# Setup the argument parser to act as the parent
parentparser = argparse.ArgumentParser(add_help=False)
#,formatter_class=CliHelpFormatter,
#                                       description=__doc__, prog='gwpy_ldvw'

# These arguments apply to all commands
parentparser.add_argument('-v', '--verbose', action='count', default=1,
                          help='increase verbose output')
parentparser.add_argument('-s', '--silent', default=False, help='show only fatal errors')

# subparsers are dependent on which action is chosen
subparsers = parser.add_subparsers(
    dest='mode', title='Actions',
    description='Select one of the following actions:')

# dictionary for subparsers
sp = dict()
actions = dict()

# -------------------------
# Add the actions and their parameters to the subparsers

# Add the subparsers for each plot product
for product in PRODUCTS:
    mod_name = product.lower()
    mod = import_module('gwpy.cli.%s' % mod_name)
    class_ = getattr(mod, product)
    prod = class_()

    # the action is the command line argument for which lot which class to call
    action = prod.get_action()
    sp[product] = subparsers.add_parser(action, help=prod.__doc__,
                                       parents=[parentparser])
    # the operation is the name of the action
    sp[product].set_defaults(func=action)
    prod.init_cli(sp[product])
    actions[action] = prod
# -----------------------------------------------------------------------------
# Run

if __name__ == '__main__':
    import os
    # if we're launched with minimum or no environment variables make some guesses
    if len(os.getenv('HOME', '')) == 0:
        os.environ['HOME'] = '/tmp/'
    # if launched from a terminal with no display
    if len(os.getenv('DISPLAY', '')) == 0:
        import matplotlib
        matplotlib.use('Agg')

    # parse the command line
    args = parser.parse_args()
    if args.silent:
        VERBOSE = 0
    else:
        VERBOSE = args.verbose
    if not args.mode:
        raise RuntimeError("Must specify action. Please try again with --help.")
    prod = actions[args.func]
    prod.log(2,('%s called' % args.func))
    result_code = prod.makePlot(args)
    # If they requested interactive mode and run from ipython this makes it easier
    if prod.is_interactive:
        from matplotlib import pyplot as plt
        plot = prod.plot
        timeseries = prod.timeseries
        ax = plot.gca()
    else:
        sys.exit(result_code)
