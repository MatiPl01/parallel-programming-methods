import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Constants for consistent styling
COLORS = {
    'static': '#4C72B0',   # Deeper blue
    'dynamic': '#DD8452',  # Orange-coral
    'guided': '#64B5CD',   # Light blue
    'ideal': '#55A868'     # Forest green
}

def save_plot(fig, filename, description):
    fig.savefig(filename, bbox_inches='tight', dpi=300)
    print(f"Saved: {os.path.basename(filename)} - {description}")

def read_csv_data(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    data = []
    current_thread = 1
    current_schedule = None
    
    for line in lines:
        line = line.strip()
        if line.startswith('Synchronous (threads:'):
            current_thread = int(line.split('threads:')[1].strip(')'))
            current_schedule = 'synchronous'
        elif line.startswith('Schedule:'):
            # Extract schedule and thread count from "Schedule: X (threads: Y)"
            parts = line.split('(')
            current_schedule = parts[0].split(':')[1].strip()
            current_thread = int(parts[1].split(':')[1].strip(')'))
        elif line.startswith('chunk_size,average_time'):
            continue
        elif ',' in line:
            chunk_size, time = map(float, line.split(','))
            data.append({
                'threads': current_thread,
                'schedule': current_schedule,
                'chunk_size': chunk_size,
                'average_time': time
            })
    
    return pd.DataFrame(data)

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

def format_axis_labels(ax):
    ax.set_xscale('log', base=2)
    ax.grid(True, which="both", ls="-", alpha=0.2)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(
        lambda x, p: f'2^{int(np.log2(x))}' if x > 0 else '0'))

def add_better_text(ax, text, y_pos=0.95):
    # Add text in top right corner, outside the plot
    ax.text(1.02, y_pos, text, 
            transform=ax.transAxes, fontsize=8,
            verticalalignment='top', color='gray',
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))

def add_better_text_to_figure(fig, text, is_single_plot=False):
    # Add text below the figure title
    if is_single_plot:
        # For single plots, position text below the title with more space
        fig.text(0.5, 0.92, f"({text})", 
                fontsize=10, color='gray',
                horizontalalignment='center', verticalalignment='top')
    else:
        # For grid plots, position text below the title
        fig.text(0.5, 0.98, f"({text})", 
                fontsize=10, color='gray',
                horizontalalignment='center', verticalalignment='top')

def plot_line_with_best_point(ax, x_data, y_data, color, label, value_suffix='s'):
    # Plot line with markers
    ax.plot(x_data, y_data, marker='o', color=color, label=label, 
            linewidth=1, markersize=3)
    
    # Find and mark best point
    if value_suffix == 's':  # For time plots, find minimum
        best_idx = y_data.idxmin()
    else:  # For speedup plots, find maximum
        best_idx = y_data.idxmax()
    
    best_x = x_data[best_idx]
    best_y = y_data[best_idx]
    
    # Plot best point markers
    ax.plot(best_x, best_y, 'o', color=color, markersize=8, alpha=0.8)
    ax.plot(best_x, best_y, 'o', color='white', markersize=4, alpha=1.0)
    
    # Add value label
    ax.text(best_x, best_y,
            f' {best_y:.2f}{value_suffix}\n 2^{int(np.log2(best_x))}',
            color=color, fontsize=8, va='bottom')

def create_execution_time_subplot(ax, thread_data, schedules, threads):
    for schedule in schedules:
        color = COLORS.get(schedule, '#000000')
        sched_data = thread_data[thread_data['schedule'] == schedule].sort_values('chunk_size')
        if not sched_data.empty:  # Only plot if we have data for this schedule
            plot_line_with_best_point(ax, sched_data['chunk_size'], sched_data['average_time'],
                                    color, schedule.capitalize(), 's')
    
    plt.yscale('log', base=2)
    ax.set_title(f'Execution Time ({threads} thread{"s" if threads > 1 else ""})')
    ax.set_xlabel('Chunk Size')
    ax.set_ylabel('Time (seconds)')
    ax.legend()
    format_axis_labels(ax)

def create_execution_time_plots(data, thread_counts, schedules):
    fig = plt.figure(figsize=(15, 10))
    
    for i, threads in enumerate(thread_counts, 0):
        ax = plt.subplot(2, 4, i + 1)
        thread_data = data[data['threads'] == threads]
        create_execution_time_subplot(ax, thread_data, schedules, threads)

    plt.suptitle('Execution Time Comparison: Different Scheduling Strategies', y=1.02)
    add_better_text_to_figure(fig, "Less is better ↓", is_single_plot=False)
    plt.tight_layout()
    return fig

def create_speedup_subplot(ax, thread_data, schedules, best_seq_time, threads):
    for schedule in schedules:
        color = COLORS.get(schedule, '#000000')
        sched_data = thread_data[thread_data['schedule'] == schedule].sort_values('chunk_size')
        if not sched_data.empty:  # Only plot if we have data for this schedule
            speedups = best_seq_time / sched_data['average_time']
            plot_line_with_best_point(ax, sched_data['chunk_size'], speedups,
                                    color, schedule.capitalize(), 'x')
    
    # Add ideal speedup line
    ax.axhline(y=threads, color=COLORS['ideal'], linestyle='--',
               label='Ideal speedup', alpha=0.5)
    
    ax.set_title(f'Speedup ({threads} threads)')
    ax.set_xlabel('Chunk Size')
    ax.set_ylabel('Speedup')
    ax.set_ylim(0, threads * 1.2)
    ax.legend()
    format_axis_labels(ax)

def create_speedup_plots(data, thread_counts, schedules, best_seq_time):
    fig = plt.figure(figsize=(15, 10))
    
    for i, threads in enumerate(thread_counts[1:], 1):  # Skip 1 thread
        ax = plt.subplot(2, 4, i)
        thread_data = data[data['threads'] == threads]
        create_speedup_subplot(ax, thread_data, schedules, best_seq_time, threads)

    plt.suptitle('Speedup Comparison: Different Scheduling Strategies', y=1.02)
    add_better_text_to_figure(fig, "More is better ↑", is_single_plot=False)
    plt.tight_layout()
    return fig

def create_speedup_bar_plot(df_combined, thread_counts, schedules):
    fig = plt.figure(figsize=(12, 6))
    
    # Prepare data
    bar_width = 0.8 / len(schedules)
    r = np.arange(len(thread_counts))
    
    # Create bars for each schedule
    for i, schedule in enumerate(schedules):
        schedule_data = df_combined[df_combined['Scheduling'] == schedule]
        if not schedule_data.empty:  # Only plot if we have data for this schedule
            color = COLORS.get(schedule, '#000000')
            
            # Create array of positions and values
            positions = []
            values = []
            for j, thread in enumerate(thread_counts):
                thread_data = schedule_data[schedule_data['Threads'] == thread]
                if not thread_data.empty:
                    positions.append(r[j] + i * bar_width)
                    values.append(thread_data.iloc[0]['Speedup'])
            
            if positions:  # Only plot if we have any data points
                plt.bar(positions, values, width=bar_width, 
                        label=schedule.capitalize(), color=color, alpha=0.8)
                
                # Add value labels and chunk sizes
                for pos, val, chunk_size in zip(positions, values, schedule_data['Best Chunk Size']):
                    plt.text(pos, val, 
                            f'{val:.2f}x\n2^{int(np.log2(chunk_size))}', 
                            ha='center', va='bottom', fontsize=8)
    
    # Add ideal speedup line
    plt.plot(r + (len(schedules) - 1) * bar_width / 2, thread_counts, '--', 
            color=COLORS['ideal'], label='Ideal', alpha=0.5)
    
    plt.xlabel('Number of Threads')
    plt.ylabel('Speedup')
    plt.title('Best Speedup Comparison with Optimal Chunk Sizes')
    plt.xticks(r + (len(schedules) - 1) * bar_width / 2, thread_counts)
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    plt.legend()
    
    add_better_text_to_figure(fig, "More is better ↑", is_single_plot=True)
    plt.tight_layout()
    return fig

def create_execution_time_bar_plot(df_combined, thread_counts, schedules):
    fig = plt.figure(figsize=(12, 6))
    
    # Prepare data
    bar_width = 0.8 / len(schedules)
    r = np.arange(len(thread_counts))
    
    # Create bars for each schedule
    for i, schedule in enumerate(schedules):
        schedule_data = df_combined[df_combined['Scheduling'] == schedule]
        if not schedule_data.empty:  # Only plot if we have data for this schedule
            color = COLORS.get(schedule, '#000000')
            
            # Create array of positions and values
            positions = []
            values = []
            for j, thread in enumerate(thread_counts):
                thread_data = schedule_data[schedule_data['Threads'] == thread]
                if not thread_data.empty:
                    positions.append(r[j] + i * bar_width)
                    values.append(thread_data.iloc[0]['Execution Time'])
            
            if positions:  # Only plot if we have any data points
                plt.bar(positions, values, width=bar_width, 
                        label=schedule.capitalize(), color=color, alpha=0.8)
                
                # Add value labels and chunk sizes
                for pos, val, chunk_size in zip(positions, values, schedule_data['Best Chunk Size']):
                    plt.text(pos, val, 
                            f'{val:.2f}s\n2^{int(np.log2(chunk_size))}', 
                            ha='center', va='bottom', fontsize=8)
    
    plt.xlabel('Number of Threads')
    plt.ylabel('Time (seconds)')
    plt.title('Best Execution Time Comparison with Optimal Chunk Sizes')
    plt.xticks(r + (len(schedules) - 1) * bar_width / 2, thread_counts)
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    plt.legend()
    
    add_better_text_to_figure(fig, "Less is better ↓", is_single_plot=True)
    plt.tight_layout()
    return fig

if __name__ == "__main__":
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(os.path.join(script_dir, 'results'), exist_ok=True)
    
    data = read_csv_data(os.path.join(script_dir, 'data'))
    thread_counts = sorted(data['threads'].unique())
    schedules = sorted(data['schedule'].unique())
    
    print(f"Found schedules: {schedules}")
    
    best_seq_time = data[data['threads'] == 1]['average_time'].min()
    print(f"Best sequential time: {best_seq_time:.6f} seconds")
    
    setup_plot_style()
    
    # Create and save execution time plots
    fig_exec_time = create_execution_time_plots(data, thread_counts, schedules)
    save_plot(fig_exec_time, os.path.join(script_dir, 'results', 'execution_time_vs_chunk.png'), 
              'Execution time plots with marked best results')
    
    # Create and save speedup plots
    fig_speedup = create_speedup_plots(data, thread_counts, schedules, best_seq_time)
    save_plot(fig_speedup, os.path.join(script_dir, 'results', 'speedup_vs_chunk.png'), 
              'Speedup comparison plots')
    
    # Prepare best results data
    best_results = []
    for threads in thread_counts:
        thread_data = data[data['threads'] == threads]
        
        for schedule in schedules:
            sched_data = thread_data[thread_data['schedule'] == schedule]
            if not sched_data.empty:  # Only process if we have data for this schedule
                best_idx = sched_data['average_time'].idxmin()
                best_config = sched_data.loc[best_idx]
                speedup = best_seq_time / best_config['average_time']
                
                best_results.append({
                    'Scheduling': schedule,
                    'Threads': threads,
                    'Best Chunk Size': best_config['chunk_size'],
                    'Execution Time': best_config['average_time'],
                    'Speedup': speedup,
                    'Efficiency': speedup / threads if threads > 0 else 0
                })
    
    # Create and save best results DataFrame
    df_best = pd.DataFrame(best_results)
    csv_path = os.path.join(script_dir, 'results', 'best_results.csv')
    df_best.to_csv(csv_path, index=False, float_format='%.3f')
    print("Saved: best_results.csv - Detailed results table")
    
    # Create and save best results bar plots
    fig_speedup_bars = create_speedup_bar_plot(df_best, thread_counts, schedules)
    save_plot(fig_speedup_bars, os.path.join(script_dir, 'results', 'best_speedup_bars.png'), 
              'Bar plot of best speedups')
    
    fig_time_bars = create_execution_time_bar_plot(df_best, thread_counts, schedules)
    save_plot(fig_time_bars, os.path.join(script_dir, 'results', 'best_time_bars.png'), 
              'Bar plot of best execution times')
