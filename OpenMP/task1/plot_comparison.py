import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Constants for consistent styling
STATIC_COLOR = '#4C72B0'  # Deeper blue
DYNAMIC_COLOR = '#DD8452'  # Orange-coral
IDEAL_COLOR = '#55A868'    # Forest green

def read_csv_data(filename):
    """Read and parse the CSV data file."""
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    data = []
    current_thread = None
    current_schedule = None
    
    for line in lines:
        line = line.strip()
        if line.startswith('Running with'):
            current_thread = int(line.split()[2])
        elif line.startswith('Schedule:'):
            current_schedule = line.split()[1]
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

def create_execution_time_plots(data, thread_counts):
    """Create execution time vs chunk size plots for all thread counts."""
    fig = plt.figure(figsize=(15, 10))
    
    for i, threads in enumerate(thread_counts, 0):
        ax = plt.subplot(2, 4, i + 1)
        thread_data = data[data['threads'] == threads]
        
        # Plot for each scheduling type
        for schedule, color, marker in [('static', STATIC_COLOR, 'o'), ('dynamic', DYNAMIC_COLOR, 's')]:
            sched_data = thread_data[thread_data['schedule'] == schedule].sort_values('chunk_size')
            
            # Plot line
            plt.plot(sched_data['chunk_size'], sched_data['average_time'], 
                    marker=marker, color=color, label=schedule.capitalize(), 
                    linewidth=1, markersize=3)
            
            # Mark best result with a dot and circle
            best_point = sched_data.loc[sched_data['average_time'].idxmin()]
            plt.plot(best_point['chunk_size'], best_point['average_time'], 'o',
                    color=color, markersize=8, alpha=0.8)
            plt.plot(best_point['chunk_size'], best_point['average_time'], 'o',
                    color='white', markersize=4, alpha=1.0)
            plt.text(best_point['chunk_size'], best_point['average_time'],
                    f' {best_point["average_time"]:.2f}s\n 2^{int(np.log2(best_point["chunk_size"]))}',
                    color=color, fontsize=8, va='bottom')
        
        plt.xscale('log', base=2)
        plt.yscale('log', base=2)  # Log scale for y-axis to better show differences
        plt.title(f'Execution Time ({threads} thread{"s" if threads > 1 else ""})')
        plt.xlabel('Chunk Size')
        plt.ylabel('Time (seconds)')
        plt.legend()
        
        # Add "less is better" annotation
        plt.text(0.02, 0.98, 'Less is better ↓', 
                transform=ax.transAxes, fontsize=8, 
                verticalalignment='top', color='gray')
        
        # Format x-axis labels
        ax.xaxis.set_major_formatter(plt.FuncFormatter(
            lambda x, p: f'2^{int(np.log2(x))}' if x > 0 else '0'))
        
        # Grid for both major and minor ticks
        plt.grid(True, which="both", ls="-", alpha=0.2)

    plt.suptitle('Execution Time Comparison: Static vs Dynamic Scheduling', y=1.02)
    plt.tight_layout()
    return fig

def create_speedup_plots(data, thread_counts, best_seq_time):
    """Create speedup comparison plots for different thread counts."""
    fig = plt.figure(figsize=(15, 10))
    
    for i, threads in enumerate(thread_counts[1:], 1):  # Skip 1 thread
        plt.subplot(2, 4, i)
        thread_data = data[data['threads'] == threads]
        
        # Calculate and plot speedups for each scheduling type
        for schedule, color, marker in [('static', STATIC_COLOR, 'o'), ('dynamic', DYNAMIC_COLOR, 's')]:
            sched_data = thread_data[thread_data['schedule'] == schedule].sort_values('chunk_size')
            speedups = best_seq_time / sched_data['average_time']
            
            plt.plot(sched_data['chunk_size'], speedups, 
                    marker=marker, color=color, label=schedule.capitalize(), 
                    linewidth=1, markersize=3)
            
            # Mark best speedup with a dot and circle
            best_point_idx = speedups.idxmax()
            best_speedup = speedups[best_point_idx]
            best_chunk = sched_data.loc[best_point_idx, 'chunk_size']
            plt.plot(best_chunk, best_speedup, 'o', color=color, markersize=8)
            plt.plot(best_chunk, best_speedup, 'o', color='white', markersize=4)
            plt.text(best_chunk, best_speedup,
                    f' {best_speedup:.2f}x\n 2^{int(np.log2(best_chunk))}',
                    color=color, fontsize=8, va='bottom')
        
        # Add ideal speedup line
        plt.axhline(y=threads, color=IDEAL_COLOR, linestyle='--', 
                   label='Ideal speedup', alpha=0.5)
        
        plt.xscale('log', base=2)
        plt.grid(True, which="both", ls="-", alpha=0.2)
        plt.title(f'Speedup ({threads} threads)')
        plt.xlabel('Chunk Size')
        plt.ylabel('Speedup')
        plt.legend()
        plt.ylim(0, threads * 1.2)
        
        # Add "more is better" annotation
        plt.text(0.02, 0.98, 'More is better ↑', 
                transform=plt.gca().transAxes, fontsize=8, 
                verticalalignment='top', color='gray')
        
        # Format x-axis labels
        plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(
            lambda x, p: f'2^{int(np.log2(x))}' if x > 0 else '0'))

    plt.suptitle('Speedup Comparison: Static vs Dynamic Scheduling', y=1.02)
    plt.tight_layout()
    return fig

def create_best_results_bars(df_combined, thread_counts, plot_type='speedup'):
    """Create bar plot comparing best results."""
    fig = plt.figure(figsize=(12, 6))
    
    # Prepare data
    static_data = df_combined[df_combined['Scheduling'] == 'static']
    dynamic_data = df_combined[df_combined['Scheduling'] == 'dynamic']
    
    # Set up bar positions
    bar_width = 0.35
    r1 = np.arange(len(thread_counts))
    r2 = [x + bar_width for x in r1]
    
    if plot_type == 'speedup':
        metric = 'Speedup'
        title = 'Best Speedup Comparison with Optimal Chunk Sizes'
        better_text = 'More is better ↑'
    else:  # execution time
        metric = 'Execution Time'
        title = 'Best Execution Time Comparison with Optimal Chunk Sizes'
        better_text = 'Less is better ↓'
    
    # Create bars
    plt.bar(r1, static_data[metric], width=bar_width, 
            label='Static', color=STATIC_COLOR, alpha=0.8)
    plt.bar(r2, dynamic_data[metric], width=bar_width, 
            label='Dynamic', color=DYNAMIC_COLOR, alpha=0.8)
    
    if plot_type == 'speedup':
        # Add ideal speedup line
        plt.plot(r1 + bar_width/2, thread_counts, '--', 
                color=IDEAL_COLOR, label='Ideal', alpha=0.5)
    
    # Add value labels and chunk sizes
    for i in range(len(thread_counts)):
        # Static scheduling
        plt.text(r1[i], static_data.iloc[i][metric], 
                f'{static_data.iloc[i][metric]:.2f}{"x" if plot_type == "speedup" else "s"}\n2^{int(np.log2(static_data.iloc[i]["Best Chunk Size"]))}', 
                ha='center', va='bottom', fontsize=8)
        # Dynamic scheduling
        plt.text(r2[i], dynamic_data.iloc[i][metric], 
                f'{dynamic_data.iloc[i][metric]:.2f}{"x" if plot_type == "speedup" else "s"}\n2^{int(np.log2(dynamic_data.iloc[i]["Best Chunk Size"]))}', 
                ha='center', va='bottom', fontsize=8)
    
    plt.xlabel('Number of Threads')
    plt.ylabel(metric + (' (seconds)' if plot_type == 'time' else ''))
    plt.title(title)
    plt.xticks(r1 + bar_width/2, thread_counts)
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    plt.legend()
    
    # Add "better" annotation
    plt.text(0.02, 0.98, better_text, 
            transform=plt.gca().transAxes, fontsize=8, 
            verticalalignment='top', color='gray')
    
    plt.tight_layout()
    return fig

def main():
    # Create results directory
    os.makedirs('results', exist_ok=True)
    
    # Read and process data
    data = read_csv_data('data/data.csv')
    thread_counts = sorted(data['threads'].unique())
    
    # Find best sequential time
    best_seq_time = data[data['threads'] == 1]['average_time'].min()
    print(f"Best sequential time: {best_seq_time:.6f} seconds")
    
    # Set up plot style
    setup_plot_style()
    
    # Create and save execution time plots
    fig_exec_time = create_execution_time_plots(data, thread_counts)
    fig_exec_time.savefig('results/execution_time_vs_chunk.png', 
                         bbox_inches='tight', dpi=300)
    
    # Create and save speedup plots
    fig_speedup = create_speedup_plots(data, thread_counts, best_seq_time)
    fig_speedup.savefig('results/speedup_vs_chunk.png', 
                        bbox_inches='tight', dpi=300)
    
    # Prepare best results data
    best_results = []
    for threads in thread_counts:
        thread_data = data[data['threads'] == threads]
        
        # Find best configurations
        for schedule in ['static', 'dynamic']:
            sched_data = thread_data[thread_data['schedule'] == schedule]
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
    df_best.to_csv('results/best_results.csv', index=False, float_format='%.3f')
    
    # Create and save best results bar plots
    fig_speedup_bars = create_best_results_bars(df_best, thread_counts, plot_type='speedup')
    fig_speedup_bars.savefig('results/best_speedup_bars.png', 
                            bbox_inches='tight', dpi=300)
    
    fig_time_bars = create_best_results_bars(df_best, thread_counts, plot_type='time')
    fig_time_bars.savefig('results/best_time_bars.png', 
                         bbox_inches='tight', dpi=300)
    
    print("\nResults have been saved to the 'results' directory:")
    print("1. execution_time_vs_chunk.png - Execution time plots with marked best results")
    print("2. speedup_vs_chunk.png - Speedup comparison plots")
    print("3. best_speedup_bars.png - Bar plot of best speedups")
    print("4. best_time_bars.png - Bar plot of best execution times")
    print("5. best_results.csv - Detailed results table")

if __name__ == "__main__":
    main()
