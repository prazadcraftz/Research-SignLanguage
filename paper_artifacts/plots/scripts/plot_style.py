"""Publication Plot Styling Configuration for Vector PDFs and 300+ DPI PNGs."""

import matplotlib
import matplotlib.pyplot as plt

def apply_paper_style():
    # Vector font embedding and publication sizing
    matplotlib.rcParams['pdf.fonttype'] = 42
    matplotlib.rcParams['ps.fonttype'] = 42
    matplotlib.rcParams['font.family'] = 'sans-serif'
    matplotlib.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
    matplotlib.rcParams['font.size'] = 10
    matplotlib.rcParams['axes.labelsize'] = 11
    matplotlib.rcParams['axes.titlesize'] = 12
    matplotlib.rcParams['xtick.labelsize'] = 9
    matplotlib.rcParams['ytick.labelsize'] = 9
    matplotlib.rcParams['legend.fontsize'] = 9
    matplotlib.rcParams['figure.titlesize'] = 13
    matplotlib.rcParams['lines.linewidth'] = 1.8
    matplotlib.rcParams['lines.markersize'] = 6
    matplotlib.rcParams['grid.alpha'] = 0.35
    matplotlib.rcParams['grid.linestyle'] = '--'

# Colorblind-safe palette (Wong / Okabe-Ito)
PALETTE = {
    "blue": "#0072B2",
    "orange": "#D55E00",
    "green": "#009E73",
    "yellow": "#F0E442",
    "purple": "#CC79A7",
    "cyan": "#56B4E9",
    "dark_gray": "#333333",
    "light_gray": "#777777"
}
