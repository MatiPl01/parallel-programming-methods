import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Constants for consistent styling
COLORS = {
    'static': '#4C72B0',   # Deeper blue
    'dynamic': '#DD8452',  # Orange-coral
    'guided': '#64B5CD',   # Light blue
    'ideal': '#55A868'     # Forest green
}

def read_csv_data(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    data = []
    current_schedule = None
    current_thread = None
    header = None
    current_data = []
    
    for line in lines:
        line = line.strip()
        if line.startswith('Schedule:'):
            if current_thread is not None and current_data:
                data.append(_create_dataframe(current_data, header, current_thread, current_schedule))
            current_schedule = line.split('(')[0].split(':')[1].strip()
            current_thread = int(line.split('threads:')[1].strip().rstrip(')'))
            current_data = []
        elif line.startswith('synchronous'):
            if current_thread is not None and current_data:
                data.append(_create_dataframe(current_data, header, current_thread, current_schedule))
            current_schedule = 'synchronous'
            current_thread = int(line.split('threads:')[1].strip().rstrip(')'))
            current_data = []
        elif line.startswith('array_size,average_time'):
            header = line.split(',')
        elif line and ',' in line:
            current_data.append(line.split(','))
    
    if current_data:
        data.append(_create_dataframe(current_data, header, current_thread, current_schedule))
    
    return pd.concat(data).astype({'array_size': int, 'average_time': float, 'threads': int})

def _create_dataframe(data, header, thread_count, schedule_type):
    df = pd.DataFrame(data, columns=header)
    df['threads'] = thread_count
    df['schedule'] = schedule_type
    return df

def setup_plot_style():
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
    return int(np.log2(n))

def format_axis(ax, title, xlabel, ylabel, threads=None, annotation=None):
    ax.set_xscale('log', base=2)
    ax.grid(True, which="both", ls="-", alpha=0.2)
    ax.set_title(title, pad=20)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend()
    
    if threads:
        ax.set_ylim(0, threads * 1.2)
    
    if annotation:
        ax.text(0.02, 0.98, annotation, 
                transform=ax.transAxes, fontsize=8, 
                verticalalignment='top', color='gray')
    
    # Format x-axis to show powers of 2
    ax.xaxis.set_major_formatter(plt.FuncFormatter(
        lambda x, p: f'2^{get_power_of_two(x)}' if x > 0 else '0'))

def plot_execution_time(ax, data, threads, schedule_types):
    # Plot execution time for each schedule type
    for schedule in schedule_types:
        schedule_data = data[(data['threads'] == threads) & (data['schedule'] == schedule)]
        ax.plot(schedule_data['array_size'], schedule_data['average_time'],
                marker='o', 
                color=COLORS.get(schedule, '#000000'), 
                label=schedule.capitalize(),
                linewidth=2, markersize=4, alpha=0.7)
    
    format_axis(ax, 
                f'Execution Time ({threads} thread{"s" if threads > 1 else ""})',
                'Array Size', 'Time (s)',
                annotation='Less is better ↓')

def plot_speedup(ax, data, threads, schedule_types):
    # Calculate sequential times for speedup reference using synchronous run
    seq_times = data[(data['threads'] == 1) & (data['schedule'] == 'synchronous')]
    seq_times = seq_times.set_index('array_size')['average_time']
    
    for schedule in schedule_types:
        thread_data = data[(data['threads'] == threads) & 
                          (data['schedule'] == schedule)].set_index('array_size')
        if thread_data.empty:
            print(f"No data found for schedule={schedule}, threads={threads}")
            continue
            
        speedup = seq_times / thread_data['average_time']
        
        # Plot speedup line
        ax.plot(thread_data.index, speedup,
                marker='o', 
                color=COLORS.get(schedule, '#000000'), 
                label=schedule.capitalize(),
                linewidth=2, markersize=4, alpha=0.7)
        
        # Mark and annotate best speedup point
        best_idx = speedup.idxmax()
        ax.plot(best_idx, speedup[best_idx], 'o',
                color=COLORS.get(schedule, '#000000'), markersize=8, alpha=0.8)
        ax.plot(best_idx, speedup[best_idx], 'o',
                color='white', markersize=4)
        ax.text(best_idx, speedup[best_idx],
                f' {speedup[best_idx]:.2f}x\n 2^{get_power_of_two(best_idx)}',
                color=COLORS.get(schedule, '#000000'), fontsize=8, va='bottom')
    
    # Add reference line for ideal speedup
    ax.axhline(y=threads, color=COLORS['ideal'], linestyle='--',
               label='Ideal speedup', alpha=0.5, linewidth=2)
    
    format_axis(ax,
                f'Speedup ({threads} threads)',
                'Array Size', 'Speedup',
                threads=threads,
                annotation='More is better ↑')

def create_comparison_table(data, exec_time_threads, schedule_types, largest_size):
    comparison_table = []
    
    # Get synchronous time for the largest size
    sync_time = data[(data['threads'] == 1) & 
                    (data['array_size'] == largest_size) & 
                    (data['schedule'] == 'synchronous')]['average_time'].iloc[0]
    
    for threads in exec_time_threads:
        row = {'Threads': threads}
        for schedule in schedule_types:
            # Get execution time for current thread count and schedule
            time = data[(data['threads'] == threads) & 
                       (data['array_size'] == largest_size) & 
                       (data['schedule'] == schedule)]['average_time'].iloc[0]
            
            # Calculate speedup relative to synchronous execution
            speedup = sync_time / time
            
            row[f'{schedule.capitalize()} Time (s)'] = f'{time:.6f}'
            row[f'{schedule.capitalize()} Speedup'] = f'{speedup:.3f}x'
        
        comparison_table.append(row)
    
    return pd.DataFrame(comparison_table)

if __name__ == "__main__":
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Ensure results directory exists
    results_dir = os.path.join(script_dir, 'results')
    os.makedirs(results_dir, exist_ok=True)
    
    # Load and process data
    data_file = os.path.join(script_dir, 'data')
    data = read_csv_data(data_file)
    schedule_types = sorted([s for s in data['schedule'].unique() if s != 'synchronous'])
    print("Schedule types:", schedule_types)
    setup_plot_style()
    
    # Generate execution time plots
    _, axes = plt.subplots(2, 2, figsize=(15, 12))
    axes = axes.flatten()
    
    exec_time_threads = [2, 4, 6, 8]
    for i, threads in enumerate(exec_time_threads):
        plot_execution_time(axes[i], data, threads, schedule_types)
    
    plt.suptitle(f'Execution Time Comparison: {" vs ".join(s.capitalize() for s in schedule_types)} Scheduling',
                 y=1.02, fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, 'execution_time_vs_problem_size.png'), bbox_inches='tight', dpi=300)
    
    # Generate speedup plots
    _, axes = plt.subplots(2, 2, figsize=(15, 12))
    axes = axes.flatten()
    
    speedup_threads = [2, 4, 6, 8]
    for i, threads in enumerate(speedup_threads):
        plot_speedup(axes[i], data, threads, schedule_types)
    
    plt.suptitle(f'Speedup Comparison: {" vs ".join(s.capitalize() for s in schedule_types)} Scheduling',
                 y=1.02, fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, 'speedup_comparison.png'), bbox_inches='tight', dpi=300)
    
    # Generate comparison table for largest problem size
    largest_size = data['array_size'].max()
    df_comparison = create_comparison_table(data, exec_time_threads, schedule_types, largest_size)
    df_comparison.to_csv(os.path.join(results_dir, 'comparison_table.csv'), index=False)
    
    # Print comparison table
    print(f"\nComparison Table for largest array size ({largest_size} elements):")
    print("=" * 120)
    print(df_comparison.to_string(index=False))
    print("=" * 120)
