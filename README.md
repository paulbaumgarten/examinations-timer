# Exminations Timer (Python version)

A simple Python+Pygame tool that can be used to display exam timing information to invigilators and candidates. I wrote this to replace the "impossible to read whiteboard at the front of a hall" that schools seem to continue to use.

![](img/screenshot.png)

Time remaining will be highlighted in orange at less than 30 minutes, and in red at less than 5 minutes remaining.

## Setup

Examination timings are read in from an excel spreadsheet. An example is provided in the project.

## Requirements

Minimum Python 3.6 (uses f-strings). 

The following packages are also required:

xlrd
pandas
pygame
