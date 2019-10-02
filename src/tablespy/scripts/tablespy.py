#!/usr/bin/env python

import click
import os
import yaml
import sys
import random
from ..inspector import Inspector
from ..printer import Printer

APPNAME='tablespy'
APPAUTHOR='flaxandteal'

@click.command()
@click.argument('infile')
@click.option('--art/--no-art', default=False)
@click.option('--sheet', default=None)
def cli(infile, art, sheet):
    inspector = Inspector(infile)
    printer = Printer()

    if sheet is None:
        inspections = enumerate(inspector.inspect_iter())
    else:
        sheet = int(sheet)
        inspections = [(sheet - 1, inspector.inspect(sheet))]

    for i, inspection in inspections:
        print(f"\n\n-------[SHEET {i+1}]-------")
        if art:
            printer.print_ascii_art(inspection)
        else:
            printer.print_inspection(inspection)
