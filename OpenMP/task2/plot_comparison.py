import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Constants for consistent styling
STATIC_COLOR = '#4C72B0'  # Deeper blue
DYNAMIC_COLOR = '#DD8452'  # Orange-coral
IDEAL_COLOR = '#55A868'    # Forest green

def read_csv_data(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    data = []
    current_thread = None
    header = None
    current_data = []
    
    for line in lines:
        line = line.strip()
        if line.startswith('Number of threads:'):
            if current_thread is not None:
                df = pd.DataFrame(current_data, columns=header)
                df['threads'] = current_thread
                data.append(df)
            current_thread = int(line.split(':')[1].strip())
            current_data = []
        elif line.startswith('array_size,average_time'):
            header = line.split(',')
        elif line and ',' in line:
            current_data.append(line.split(','))
    
    if current_data:
        df = pd.DataFrame(current_data, columns=header)
        df['threads'] = current_thread
        data.append(df)
    
    return pd.concat(data).astype({'array_size': int, 'average_time': float, 'threads': int})

def setup_plot_style():
    """Set up the common plot style."""
    plt.style.use('seaborn-v0_8-darkgrid')
    plt.rcParams.update({
        'font.size': 10,
        'axes.titlesize': 12,
        'axes.labelsize': 10,
        'xtick.labelsize': 8,
        'ytick.labelsize': 8,
        'legend.fontsize': 8,
        'figure.titlesize': 14
    })

def get_power_of_two(n):
    """Get the power of 2 for a number."""
    return int(np.log2(n))

# Create results directory if it doesn't exist
os.makedirs('results', exist_ok=True)

# Read the CSV files from data directory
static_data = read_csv_data('data/static.csv')
dynamic_data = read_csv_data('data/dynamic.csv')

# Set up plot style
setup_plot_style()

# Create execution time plots in 2x2 grid
fig, axes = plt.subplots(2, 2, figsize=(15, 12))
axes = axes.flatten()

exec_time_threads = [1, 2, 4, 8]  # Thread counts for execution time plot
for i, threads in enumerate(exec_time_threads):
    ax = axes[i]
    
    static_thread = static_data[static_data['threads'] == threads]
    dynamic_thread = dynamic_data[dynamic_data['threads'] == threads]
    
    # Plot with improved styling
    ax.plot(static_thread['array_size'], static_thread['average_time'], 
            marker='o', color=STATIC_COLOR, label='Static', 
            linewidth=2, markersize=4, alpha=0.7)
    ax.plot(dynamic_thread['array_size'], dynamic_thread['average_time'], 
            marker='s', color=DYNAMIC_COLOR, label='Dynamic', 
            linewidth=2, markersize=4, alpha=0.7)
    
    ax.set_xscale('log', base=2)
    ax.set_yscale('log')
    ax.grid(True, which="both", ls="-", alpha=0.2)
    ax.set_title(f'Execution Time ({threads} thread{"s" if threads > 1 else ""})', pad=20)
    ax.set_xlabel('Array Size')
    ax.set_ylabel('Time (s)')
    ax.legend()
    
    # Add "less is better" annotation
    ax.text(0.02, 0.98, 'Less is better ↓', 
            transform=ax.transAxes, fontsize=8, 
            verticalalignment='top', color='gray')
    
    # Format x-axis labels
    ax.xaxis.set_major_formatter(plt.FuncFormatter(
        lambda x, p: f'2^{get_power_of_two(x)}' if x > 0 else '0'))

plt.suptitle('Execution Time Comparison: Static vs Dynamic Scheduling', y=1.02, fontsize=14)
plt.tight_layout()
plt.savefig('results/execution_time_vs_problem_size.png', bbox_inches='tight', dpi=300)

# Create speedup plots in 2x2 grid
fig, axes = plt.subplots(2, 2, figsize=(15, 12))
axes = axes.flatten()

# Get sequential times (1 thread) for each array size
static_seq = static_data[static_data['threads'] == 1].set_index('array_size')['average_time']
dynamic_seq = dynamic_data[dynamic_data['threads'] == 1].set_index('array_size')['average_time']

speedup_threads = [2, 4, 6, 8]  # Thread counts for speedup plots
for i, threads in enumerate(speedup_threads):
    ax = axes[i]
    
    static_thread = static_data[static_data['threads'] == threads].set_index('array_size')
    dynamic_thread = dynamic_data[dynamic_data['threads'] == threads].set_index('array_size')
    
    # Calculate speedup relative to the same array size in sequential execution
    static_speedup = static_seq / static_thread['average_time']
    dynamic_speedup = dynamic_seq / dynamic_thread['average_time']
    
    # Plot with improved styling
    ax.plot(static_thread.index, static_speedup, 
            marker='o', color=STATIC_COLOR, label='Static', 
            linewidth=2, markersize=4, alpha=0.7)
    ax.plot(dynamic_thread.index, dynamic_speedup, 
            marker='s', color=DYNAMIC_COLOR, label='Dynamic', 
            linewidth=2, markersize=4, alpha=0.7)
    
    # Mark best speedups with dot+circle
    static_best_idx = static_speedup.idxmax()
    dynamic_best_idx = dynamic_speedup.idxmax()
    
    # Plot best points for static
    ax.plot(static_best_idx, static_speedup[static_best_idx], 'o',
            color=STATIC_COLOR, markersize=8, alpha=0.8)
    ax.plot(static_best_idx, static_speedup[static_best_idx], 'o',
            color='white', markersize=4)
    ax.text(static_best_idx, static_speedup[static_best_idx],
            f' {static_speedup[static_best_idx]:.2f}x\n 2^{get_power_of_two(static_best_idx)}',
            color=STATIC_COLOR, fontsize=8, va='bottom')
    
    # Plot best points for dynamic
    ax.plot(dynamic_best_idx, dynamic_speedup[dynamic_best_idx], 'o',
            color=DYNAMIC_COLOR, markersize=8, alpha=0.8)
    ax.plot(dynamic_best_idx, dynamic_speedup[dynamic_best_idx], 'o',
            color='white', markersize=4)
    ax.text(dynamic_best_idx, dynamic_speedup[dynamic_best_idx],
            f' {dynamic_speedup[dynamic_best_idx]:.2f}x\n 2^{get_power_of_two(dynamic_best_idx)}',
            color=DYNAMIC_COLOR, fontsize=8, va='bottom')
    
    # Add ideal speedup line with improved styling
    ax.axhline(y=threads, color=IDEAL_COLOR, linestyle='--', 
               label='Ideal speedup', alpha=0.5, linewidth=2)
    
    ax.set_xscale('log', base=2)
    ax.grid(True, which="both", ls="-", alpha=0.2)
    ax.set_title(f'Speedup ({threads} threads)', pad=20)
    ax.set_xlabel('Array Size')
    ax.set_ylabel('Speedup')
    ax.legend()
    
    # Set y-axis limits to show up to ideal speedup with some padding
    ax.set_ylim(0, threads * 1.2)
    
    # Add "more is better" annotation
    ax.text(0.02, 0.98, 'More is better ↑', 
            transform=ax.transAxes, fontsize=8, 
            verticalalignment='top', color='gray')
    
    # Format x-axis labels
    ax.xaxis.set_major_formatter(plt.FuncFormatter(
        lambda x, p: f'2^{get_power_of_two(x)}' if x > 0 else '0'))

plt.suptitle('Speedup Comparison: Static vs Dynamic Scheduling', y=1.02, fontsize=14)
plt.tight_layout()
plt.savefig('results/speedup_comparison.png', bbox_inches='tight', dpi=300)

# Print comparison table for the largest array size
largest_size = 1073741824
comparison_table = []

for threads in exec_time_threads:
    static_time = static_data[(static_data['threads'] == threads) & 
                            (static_data['array_size'] == largest_size)]['average_time'].iloc[0]
    dynamic_time = dynamic_data[(dynamic_data['threads'] == threads) & 
                               (dynamic_data['array_size'] == largest_size)]['average_time'].iloc[0]
    
    # Calculate speedup relative to sequential execution
    static_speedup = static_data[(static_data['threads'] == 1) & 
                               (static_data['array_size'] == largest_size)]['average_time'].iloc[0] / static_time
    dynamic_speedup = dynamic_data[(dynamic_data['threads'] == 1) & 
                                 (dynamic_data['array_size'] == largest_size)]['average_time'].iloc[0] / dynamic_time
    
    comparison_table.append({
        'Threads': threads,
        'Static Time (s)': f'{static_time:.6f}',
        'Dynamic Time (s)': f'{dynamic_time:.6f}',
        'Static Speedup': f'{static_speedup:.3f}x',
        'Dynamic Speedup': f'{dynamic_speedup:.3f}x'
    })

# Save comparison table to CSV and print it
df_comparison = pd.DataFrame(comparison_table)
df_comparison.to_csv('results/comparison_table.csv', index=False)

# Print the table in a nice format
print("\nComparison Table for largest array size (1073741824 elements):")
print("=" * 100)
print(df_comparison.to_string(index=False))
print("=" * 100)