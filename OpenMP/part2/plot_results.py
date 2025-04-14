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

PHASE_LABELS = {
    'random_time': 'Random Generation',
    'distribute_time': 'Distribution',
    'sort_time': 'Sorting',
    'rewrite_time': 'Rewriting',
    'total_time': 'Total'
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
        'lines.markersize': 8,
        'figure.facecolor': 'white',
        'axes.facecolor': '#F0F0F0'
    })

def get_data_params(df):
    # Extract key parameters from the data
    return {
        'array_sizes': sorted(df['array_size'].unique()),
        'thread_counts': sorted(df['num_threads'].unique()),
        'bucket_sizes': sorted(df['bucket_capacity'].unique())
    }

def print_timing_table(data, bucket_size):
    # Print timing information in a formatted table
    print(f"\nBucket size {bucket_size}:")
    print("Threads  Random  Distrib   Sort    Rewrite   Total")
    print("-" * 50)
    
    for _, row in data.iterrows():
        print(f"{int(row['num_threads']):4d}    {row['random_time']:.3f}   {row['distribute_time']:.3f}   "
              f"{row['sort_time']:.3f}   {row['rewrite_time']:.3f}   {row['total_time']:.3f}")

def plot_stacked_bars(ax, data, thread_counts, bucket_size):
    # Plot stacked bar chart for execution time breakdown
    phases = ['random_time', 'distribute_time', 'sort_time', 'rewrite_time']
    
    # Calculate mean times for each phase and thread count
    mean_times = pd.DataFrame(index=thread_counts)
    for phase in phases:
        mean_times[phase] = [data[data['num_threads'] == t][phase].mean() 
                           for t in thread_counts]
    
    # Plot stacked bars
    x_pos = np.arange(len(thread_counts))
    bottom = np.zeros(len(thread_counts))
    for phase in phases:
        ax.bar(x_pos, mean_times[phase],
              width=0.8,
              bottom=bottom, 
              label=PHASE_LABELS[phase],
              color=COLORS[phase])
        bottom += mean_times[phase]
    
    # Add total time labels
    total_times = mean_times.sum(axis=1)
    for x, total in zip(x_pos, total_times):
        ax.text(x, total, f'{total:.2f}s',
               ha='center', va='bottom')
    
    return ax

def plot_execution_time_breakdown():
    params = get_data_params(df)
    largest_size = max(params['array_sizes'])
    selected_sizes = [16, 256, 4096, 65536]  # Representative bucket sizes 2^4 to 2^16
    
    # Print detailed timing information
    print(f"\nDetailed timing for array size {largest_size:,}:")
    for bucket_size in selected_sizes:
        size_data = df[
            (df['array_size'] == largest_size) & 
            (df['bucket_capacity'] == bucket_size)
        ].sort_values('num_threads')
        print_timing_table(size_data, bucket_size)
    
    # Create 2x2 grid of subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    axes = axes.flatten()
    
    # Plot each bucket size
    for ax_idx, (ax, bucket_size) in enumerate(zip(axes, selected_sizes)):
        size_data = df[
            (df['array_size'] == largest_size) & 
            (df['bucket_capacity'] == bucket_size)
        ].sort_values('num_threads')
        
        plot_stacked_bars(ax, size_data, params['thread_counts'], bucket_size)
        
        # Configure axis
        ax.set_xlabel('Number of Threads')
        if ax_idx % 2 == 0:
            ax.set_ylabel('Time (s)')
        ax.set_title(f'Bucket Size: 2^{int(np.log2(bucket_size))} ({bucket_size:,})')
        ax.grid(True, axis='y', alpha=0.3)
        ax.set_xticks(np.arange(len(params['thread_counts'])))
        ax.set_xticklabels(params['thread_counts'])
    
    # Add legend and adjust layout
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, 
              loc='center right',
              bbox_to_anchor=(0.98, 0.5))
    
    plt.suptitle(f'Execution Time Analysis\nArray Size: {largest_size:,}', y=0.95)
    plt.subplots_adjust(right=0.85, hspace=0.3, wspace=0.25)
    return fig

def plot_bucket_size_analysis():
    params = get_data_params(df)
    seq_data = df[df['num_threads'] == 1].copy()
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
    fig.patch.set_facecolor('white')
    
    # Create color map for bucket sizes
    colors = plt.colormaps['tab20'](np.linspace(0, 1, len(params['bucket_sizes'])))
    
    # Plot 1: Bucket Size vs Problem Size
    for bucket_size, color in zip(params['bucket_sizes'], colors):
        size_data = seq_data[seq_data['bucket_capacity'] == bucket_size]
        if not size_data.empty:
            ax1.plot(size_data['array_size'], 
                    [bucket_size] * len(size_data),
                    'o-', color=color, markersize=6,
                    label=f'2^{int(np.log2(bucket_size))} ({bucket_size})')
    
    ax1.set_xscale('log', base=2)
    ax1.set_yscale('log', base=2)
    ax1.set_xlabel('Problem Size (n)')
    ax1.set_ylabel('Bucket Size')
    ax1.set_title('Bucket Size vs Problem Size')
    ax1.grid(True, which='both', alpha=0.3)
    ax1.grid(True, which='minor', alpha=0.2)
    
    # Plot 2: Number of Buckets vs Problem Size
    for bucket_size, color in zip(params['bucket_sizes'], colors):
        size_data = seq_data[seq_data['bucket_capacity'] == bucket_size]
        if not size_data.empty:
            buckets_count = size_data['array_size'] / bucket_size
            ax2.plot(size_data['array_size'],
                    buckets_count,
                    'o-', color=color, markersize=6,
                    label=f'2^{int(np.log2(bucket_size))} ({bucket_size})')
    
    ax2.set_xscale('log', base=2)
    ax2.set_yscale('log', base=2)
    ax2.set_xlabel('Problem Size (n)')
    ax2.set_ylabel('Number of Buckets')
    ax2.set_title('Number of Buckets vs Problem Size')
    ax2.grid(True, which='both', alpha=0.3)
    ax2.grid(True, which='minor', alpha=0.2)
    
    # Add legend
    lines, labels = [], []
    for ax in [ax1, ax2]:
        axlines, axlabels = ax.get_legend_handles_labels()
        lines.extend(axlines)
        labels.extend(axlabels)
    
    # Remove duplicates while preserving order
    unique_labels, unique_lines = [], []
    for line, label in zip(lines, labels):
        if label not in unique_labels:
            unique_labels.append(label)
            unique_lines.append(line)
    
    fig.legend(unique_lines, unique_labels,
              bbox_to_anchor=(1.0, 0.5),
              loc='center left',
              title='Bucket Sizes (2^x)')
    
    plt.suptitle('Bucket Size Analysis\nAll configurations from 2^4 to 2^16', y=1.02)
    plt.subplots_adjust(right=0.83, wspace=0.3)
    return fig

def plot_speedup():
    params = get_data_params(df)
    largest_size = max(params['array_sizes'])
    best_bucket_size = find_best_bucket_size()
    
    # Get data for the best bucket size
    largest_data = df[
        (df['array_size'] == largest_size) & 
        (df['bucket_capacity'] == best_bucket_size)
    ].sort_values('num_threads')
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor('white')
    
    # Plot speedup for each phase
    phases = ['random_time', 'distribute_time', 'sort_time', 'rewrite_time', 'total_time']
    for phase in phases:
        seq_time = largest_data[largest_data['num_threads'] == 1][phase].iloc[0]
        speedups = []
        for threads in params['thread_counts']:
            thread_data = largest_data[largest_data['num_threads'] == threads]
            if not thread_data.empty:
                time = thread_data[phase].iloc[0]
                speedup = seq_time / time if time > 0 else 0
                speedups.append(speedup)
            else:
                speedups.append(0)
        
        ax.plot(params['thread_counts'], speedups, marker='o',
                color=COLORS[phase], label=PHASE_LABELS[phase])
    
    # Add ideal speedup line
    ax.plot(params['thread_counts'], params['thread_counts'], '--',
            color=COLORS['ideal'], label='Ideal Speedup')
    
    ax.set_xlabel('Number of Threads')
    ax.set_ylabel('Speedup')
    ax.set_title(f'Speedup Analysis\nArray Size: {largest_size:,}, Bucket Size: {int(best_bucket_size):,}')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper left')
    ax.set_xticks(params['thread_counts'])
    
    plt.tight_layout()
    return fig

def find_best_bucket_size():
    params = get_data_params(df)
    seq_data = df[df['num_threads'] == 1].copy()
    
    # Calculate average performance rank for each bucket size
    performance_ranks = []
    for bucket_size in params['bucket_sizes']:
        total_rank = 0
        count = 0
        for array_size in params['array_sizes']:
            size_data = seq_data[seq_data['array_size'] == array_size]
            if not size_data.empty:
                rank = size_data[size_data['bucket_capacity'] == bucket_size]['total_time'].iloc[0]
                total_rank += rank
                count += 1
        avg_rank = total_rank / count if count > 0 else float('inf')
        performance_ranks.append((bucket_size, avg_rank))
    
    return min(performance_ranks, key=lambda x: x[1])[0]

def save_plot(fig, filename, description):
    os.makedirs('results', exist_ok=True)
    fig.savefig(os.path.join('results', filename), bbox_inches='tight', dpi=300, facecolor='white')
    print(f"Saved: {filename} - {description}")

if __name__ == "__main__":
    setup_plot_style()
    
    plots = [
        (plot_bucket_size_analysis, 'bucket_size_analysis.png', 'Bucket size analysis'),
        (plot_execution_time_breakdown, 'execution_time_analysis.png', 'Execution time analysis'),
        (plot_speedup, 'speedup_analysis.png', 'Speedup analysis')
    ]
    
    for plot_func, filename, description in plots:
        fig = plot_func()
        save_plot(fig, filename, description)
        plt.close(fig)
