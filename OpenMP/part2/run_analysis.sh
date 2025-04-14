#!/bin/bash

# Create results directory if it doesn't exist
mkdir -p results

# Run the analysis script (it will read from run_analysis.out by default)
python3 analyze_distribution.py

echo "Analysis complete. Results saved to results/random_distribution_analysis.png"
