# Coil Generation and Evaluation Scripts

## Overview

This repository contains scripts developed for generating and evaluating cylindrical coils. The scripts are designed to facilitate the creation of coil windings and save relevant data for further analysis and optimization.

## Scripts
### /Calculations
### 1. `windings.py`

This script is responsible for generating coil windings based on specified parameters. It provides flexibility in defining the contours and configuration of the coils, allowing for efficient coil design and testing.
Used to test different coil configurations and quickly save to pkl files for fast evaluations to be used in new_main.py

#### Key Features:
- Generates coil windings with customizable parameters.
- Saves winding data for further analysis.
- Provides a foundation for integrating with other evaluation and optimization tools.

### 2. `new_main.py`

This script integrates the `windings` function with additional functionality for evaluating the generated coils. It is designed to assess the performance and efficiency of the coils based on specific criteria.

#### Key Features:
- Evaluates the generated coils based on predefined metrics.
- Provides insights into the efficiency and performance of different coil configurations.
- Supports iterative testing and optimization of coil designs.

### /opm_coil_fork
### 3. `new_coil_generation.py`

This script makes your final coils that you tested from the `windings` function. Be sure you have the same paramaters which you had used in `calculations/windings.py` to generate the same coil. And be sure your kicad header file is the correct file you want to generate from. 


## Getting Started

### Prerequisites

Ensure you have the following installed on your system:
- Python 3.8 +
- Required Python packages (listed in `requirements.txt`)

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/JKama5/SMEG.git
