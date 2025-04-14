import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Constants for consistent styling
COLORS = {
    'random_time': '#4C72B0',      # Blue
    'distribute_time': '#DD8452',   # Orange
    'sort_time': '#55A868',        # Green
    'rewrite_time': '#C44E52',     # Red
    'total_time': '#8172B3',       # Purple
    'ideal': '#000000'             # Black
}

# Load the data
df = pd.read_csv('data.csv')

def setup_plot_style():
    plt.style.use('seaborn-v0_8-darkgrid')
    plt.rcParams.update({
        'font.size': 12,
        'axes.titlesize': 14,
        'axes.labelsize': 12,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 10,
        'figure.titlesize': 16,
        'lines.linewidth': 2,
        'lines.markersize': 8
    })

def save_plot(fig, filename, description):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    fig.savefig(filename, bbox_inches='tight', dpi=300)
    print(f"Saved: {os.path.basename(filename)} - {description}")

def plot_bucket_size_analysis():
    # Create figure with subplots for different problem sizes
    problem_sizes = sorted(df['array_size'].unique())
    fig, axes = plt.subplots(2, 4, figsize=(20, 10))
    axes = axes.flatten()
    
    for idx, size in enumerate(problem_sizes[:8]):  # Only use first 8 sizes
        size_data = df[df['array_size'] == size]
        
        # Find the minimum time across all threads for this size
        min_time = size_data['total_time'].min()
        min_time_row = size_data[size_data['total_time'] == min_time].iloc[0]
        best_thread = min_time_row['num_threads']
        
        # Plot total time vs bucket size for each thread count
        thread_counts = sorted(size_data['num_threads'].unique())
        best_color = None
        for threads in thread_counts:
            thread_data = size_data[size_data['num_threads'] == threads]
            line = axes[idx].plot(thread_data['num_buckets'], thread_data['total_time'],
                         marker='o', label=f'{threads} threads')
            if threads == best_thread:
                best_color = line[0].get_color()
        
        # Plot best point markers after all lines are drawn
        axes[idx].plot(min_time_row['num_buckets'], min_time, 'o', 
                      color=best_color, markersize=8, alpha=0.8, zorder=10)
        axes[idx].plot(min_time_row['num_buckets'], min_time, 'o', 
                      color='white', markersize=4, alpha=1.0, zorder=11)
        # Add value label
        axes[idx].text(min_time_row['num_buckets'], min_time,
                      f' {min_time:.6f}s\n 2^{int(np.log2(min_time_row["num_buckets"]))}',
                      color=best_color, fontsize=8, va='bottom', zorder=12)
        
        axes[idx].set_xscale('log', base=2)
        axes[idx].set_title(f'Array Size: {size:,}')
        axes[idx].set_xlabel('Number of Buckets')
        axes[idx].set_ylabel('Total Time (s)')
        axes[idx].grid(True)
        if idx == 0:  # Only show legend on first plot
            axes[idx].legend()
    
    plt.tight_layout()
    return fig

def plot_random_distribution():
    """Plot the distribution of random numbers."""
    np.random.seed(42)  # For reproducibility
    array_size = int(1024)  # Convert to integer
    random_numbers = np.random.uniform(0, 1, array_size)
    
    plt.figure(figsize=(10, 6))
    plt.hist(random_numbers, bins=50, density=True, alpha=0.7, label='Generated Numbers')
    
    # Plot theoretical uniform distribution
    x = np.linspace(0, 1, 100)
    plt.plot(x, np.ones_like(x), 'r-', label='Theoretical Uniform')
    
    plt.title('Random Number Distribution')
    plt.xlabel('Value')
    plt.ylabel('Density')
    plt.legend()
    plt.grid(True)
    
    return plt.gcf()

def plot_execution_time_breakdown():
    # Get data for the largest problem size
    largest_size = df['array_size'].max()
    largest_data = df[df['array_size'] == largest_size]
    
    # Calculate mean times for each phase, but only for specific thread counts
    thread_counts = [1, 2, 4, 8, 12]  # Only these thread counts
    mean_times = largest_data[largest_data['num_threads'].isin(thread_counts)].groupby('num_threads').agg({
        'random_time': 'mean',
        'distribute_time': 'mean',
        'sort_time': 'mean',
        'rewrite_time': 'mean'
    }).reset_index()
    
    # Create stacked bar plot
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Create x-axis positions without gaps
    x_pos = np.arange(len(thread_counts))
    
    bottom = np.zeros(len(mean_times))
    for phase, color in COLORS.items():
        if phase != 'ideal' and phase != 'total_time':
            ax.bar(x_pos, mean_times[phase],
                  bottom=bottom, label=phase.replace('_', ' ').title(),
                  color=color)
            bottom += mean_times[phase]
    
    ax.set_xlabel('Number of Threads')
    ax.set_ylabel('Time (s)')
    ax.set_title(f'Execution Time Breakdown\nArray Size: {largest_size:,}')
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(True, axis='y')
    
    # Set x-axis ticks to show actual thread counts
    ax.set_xticks(x_pos)
    ax.set_xticklabels(thread_counts)
    
    plt.tight_layout()
    return fig

def plot_execution_time():
    # Filter for the largest problem size
    largest_size = df['array_size'].max()
    largest_data = df[df['array_size'] == largest_size]
    
    # Group by number of threads and calculate mean for each metric
    grouped_data = largest_data.groupby('num_threads').agg({
        'random_time': 'mean',
        'distribute_time': 'mean',
        'sort_time': 'mean',
        'rewrite_time': 'mean',
        'total_time': 'mean'
    }).reset_index()
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Plot each part
    parts = ['random_time', 'distribute_time', 'sort_time', 'rewrite_time', 'total_time']
    labels = ['Random Generation', 'Distribution', 'Sorting', 'Rewriting', 'Total']
    
    for part, label in zip(parts, labels):
        ax.plot(grouped_data['num_threads'], grouped_data[part], 
                marker='o', color=COLORS[part], label=label)
    
    ax.set_xlabel('Number of Processors')
    ax.set_ylabel('Execution Time (seconds)')
    ax.set_title(f'Execution Time vs. Number of Processors\nArray Size: {largest_size:,}')
    
    # Set x-ticks to only show the actual thread counts
    ax.set_xticks(grouped_data['num_threads'])
    
    # Add grid
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Add legend
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.tight_layout()
    return fig

def plot_speedup():
    # Filter for the largest problem size
    largest_size = df['array_size'].max()
    largest_data = df[df['array_size'] == largest_size]
    
    # Group by number of threads and calculate mean for each metric
    grouped_data = largest_data.groupby('num_threads').agg({
        'random_time': 'mean',
        'distribute_time': 'mean',
        'sort_time': 'mean',
        'rewrite_time': 'mean',
        'total_time': 'mean'
    }).reset_index()
    
    # Get sequential times (with 1 thread)
    seq_times = grouped_data[grouped_data['num_threads'] == 1].iloc[0]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Plot speedup for each part
    parts = ['random_time', 'distribute_time', 'sort_time', 'rewrite_time', 'total_time']
    labels = ['Random Generation', 'Distribution', 'Sorting', 'Rewriting', 'Total']
    
    for part, label in zip(parts, labels):
        speedup = seq_times[part] / grouped_data[part]
        ax.plot(grouped_data['num_threads'], speedup, 
                marker='o', color=COLORS[part], label=label)
    
    # Add ideal speedup line
    max_threads = grouped_data['num_threads'].max()
    ax.plot([1, max_threads], [1, max_threads], '--', 
            color=COLORS['ideal'], label='Ideal Speedup')
    
    ax.set_xlabel('Number of Processors')
    ax.set_ylabel('Speedup')
    ax.set_title(f'Speedup vs. Number of Processors\nArray Size: {largest_size:,}')
    
    # Set x-ticks to only show the actual thread counts
    ax.set_xticks(grouped_data['num_threads'])
    
    # Add grid
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Add legend
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.tight_layout()
    return fig

if __name__ == "__main__":
    # Setup plotting style
    setup_plot_style()
    
    # Create results directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(script_dir, 'results')
    os.makedirs(results_dir, exist_ok=True)
    
    # Generate and save all plots
    plots = [
        (plot_bucket_size_analysis, 'bucket_size_analysis.png', 'Bucket size analysis for different problem sizes'),
        (plot_execution_time_breakdown, 'execution_time_breakdown.png', 'Execution time breakdown by phase'),
        (plot_execution_time, 'execution_time.png', 'Execution time of algorithm parts vs. number of processors'),
        (plot_speedup, 'speedup.png', 'Speedup vs. number of processors for different algorithm parts')
    ]
    
    for plot_func, filename, description in plots:
        fig = plot_func()
        save_plot(fig, os.path.join(results_dir, filename), description)
        plt.close(fig)
