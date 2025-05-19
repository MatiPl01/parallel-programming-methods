import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def setup_plotting_style():
    """Set up the plotting style and create results directory."""
    # Use seaborn's recommended way to set the style
    sns.set_theme(style="whitegrid")
    
    # Create results directory if it doesn't exist
    results_dir = Path('results')
    results_dir.mkdir(exist_ok=True)
    return results_dir

def load_and_prepare_data(csv_path):
    """Load and prepare the data for analysis."""
    df = pd.read_csv(csv_path)
    df['time'] = pd.to_numeric(df['time'], errors='coerce')
    # Ensure dataSize is categorical and sorted
    df['dataSize'] = pd.Categorical(df['dataSize'], categories=['1G', '5G', '10G'], ordered=True)
    return df

def calculate_mean_times(df):
    """Calculate mean times for each configuration and data size."""
    return df.groupby(['dataSize', 'confId'])['time'].mean().reset_index()

def calculate_hadoop_speedup(mean_times):
    """Calculate speedup for Hadoop configs: seq_strong/hadoop_strong and seq_weak/hadoop_weak."""
    # Pivot for easier matching
    pivot = mean_times.pivot(index='dataSize', columns='confId', values='time')
    speedup = pd.DataFrame(index=pivot.index)
    if 'seq_strong' in pivot.columns and 'hadoop_strong' in pivot.columns:
        speedup['hadoop_strong'] = pivot['seq_strong'] / pivot['hadoop_strong']
    if 'seq_weak' in pivot.columns and 'hadoop_weak' in pivot.columns:
        speedup['hadoop_weak'] = pivot['seq_weak'] / pivot['hadoop_weak']
    speedup = speedup.reset_index().melt(id_vars='dataSize', var_name='confId', value_name='speedup')
    return speedup

def plot_computation_times(mean_times, results_dir):
    """Grouped bar plot: x-axis=problem size, bars=configuration."""
    plt.figure(figsize=(8, 6))
    ax = sns.barplot(
        data=mean_times,
        x='dataSize',
        y='time',
        hue='confId',
        palette='husl',
        errorbar=None
    )
    plt.title('Mean Computation Time by Problem Size and Configuration')
    plt.xlabel('Problem Size (dataSize)')
    plt.ylabel('Mean Time (seconds)')
    plt.legend(title='Configuration')
    for container in ax.containers:
        ax.bar_label(container, fmt='%.1f', label_type='edge')
    plt.tight_layout()
    plt.savefig(results_dir / 'computation_times.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_speedup_hadoop(speedup_df, results_dir):
    """Line plot: x-axis=problem size, y-axis=speedup, only Hadoop configs."""
    plt.figure(figsize=(8, 6))
    sns.lineplot(
        data=speedup_df,
        x='dataSize',
        y='speedup',
        hue='confId',
        marker='o',
        palette='husl'
    )
    plt.title('Hadoop Speedup vs Problem Size')
    plt.xlabel('Problem Size (dataSize)')
    plt.ylabel('Speedup (seq/hadoop, matching hardware)')
    plt.axhline(y=1, color='r', linestyle='--', alpha=0.3)
    plt.legend(title='Configuration')
    plt.tight_layout()
    plt.savefig(results_dir / 'speedup.png', dpi=300, bbox_inches='tight')
    plt.close()

def main():
    """Main function to run the analysis and create plots."""
    # Setup
    results_dir = setup_plotting_style()
    
    # Load and prepare data
    df = load_and_prepare_data('results.csv')
    mean_times = calculate_mean_times(df)
    speedup_df = calculate_hadoop_speedup(mean_times)
    
    # Create plots
    plot_computation_times(mean_times, results_dir)
    plot_speedup_hadoop(speedup_df, results_dir)

if __name__ == "__main__":
    main() 