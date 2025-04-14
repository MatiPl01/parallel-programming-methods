#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import sys
import os
import re

def read_numbers_from_file(filename):
    """Read numbers from the output file, extracting them from any text content."""
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    
    numbers = []
    with open(filename, 'r') as f:
        for line in f:
            # Use regex to find numbers in the line
            nums = re.findall(r'\b\d+\b', line)
            numbers.extend(int(num) for num in nums)
    
    if not numbers:
        print("Error: No numbers found in the file.")
        sys.exit(1)
        
    return np.array(numbers)

def analyze_distribution(numbers):
    # Basic statistics
    print(f"Number of samples: {len(numbers)}")
    print(f"Mean: {np.mean(numbers):.2f}")
    print(f"Standard deviation: {np.std(numbers):.2f}")
    print(f"Min: {np.min(numbers)}")
    print(f"Max: {np.max(numbers)}")
    
    # Create a figure with multiple subplots
    fig = plt.figure(figsize=(15, 10))
    
    # Histogram
    ax1 = fig.add_subplot(221)
    ax1.hist(numbers, bins=50, density=True, alpha=0.7)
    ax1.set_title('Histogram of Random Numbers')
    ax1.set_xlabel('Value')
    ax1.set_ylabel('Density')
    
    # Q-Q plot
    ax2 = fig.add_subplot(222)
    stats.probplot(numbers, dist="norm", plot=ax2)
    ax2.set_title('Q-Q Plot')
    
    # Box plot
    ax3 = fig.add_subplot(223)
    ax3.boxplot(numbers)
    ax3.set_title('Box Plot')
    
    # Time series plot (first 1000 points)
    ax4 = fig.add_subplot(224)
    ax4.plot(numbers[:1000])
    ax4.set_title('Time Series (first 1000 points)')
    ax4.set_xlabel('Index')
    ax4.set_ylabel('Value')
    
    plt.tight_layout()
    
    # Create results directory if it doesn't exist
    os.makedirs('results', exist_ok=True)
    
    # Save the plot to the results directory
    plt.savefig('results/random_distribution_analysis.png')
    plt.close()

if __name__ == "__main__":
    # Use run_analysis.out as the default input file
    filename = 'run_analysis.out'
    numbers = read_numbers_from_file(filename)
    analyze_distribution(numbers) 