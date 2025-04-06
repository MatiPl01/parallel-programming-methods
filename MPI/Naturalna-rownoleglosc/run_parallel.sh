#!/bin/bash -l
#SBATCH --job-name=pi_scal_experiments
#SBATCH --output=pi_scal_%j.out
#SBATCH --error=pi_scal_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=12
#SBATCH --time=12:00:00
#SBATCH --partition=plgrid
#SBATCH --account=plgmpr25-cpu

module add .plgrid plgrid/tools/openmpi
module load plgrid/tools/openmpi

mpicc -o pi_parallel pi_parallel.c

# Define problem sizes
SMALL=100000      # Small problem
MEDIUM=10000000   # Medium problem
LARGE=10000000000 # Large problem

# Number of repetitions per experiment
REPEATS=10

# Function to run experiments
run_experiment() {
  local scaling=$1
  local size_desc=$2
  local points=$3
  local output_file="results_${scaling}_scaling_${size_desc}.csv"

  echo "Processors,Time (s)" >$output_file # CSV header

  for procs in {1..12}; do
    total_time=0
    for run in $(seq 1 $REPEATS); do
      if [[ "$scaling" == "strong" ]]; then
        effective_points=$points
      else
        effective_points=$((points * procs))
      fi

      # Collect execution time from C program
      time_taken=$(mpiexec -np $procs ./pi_parallel $effective_points)

      # Sum for averaging later
      total_time=$(echo "$total_time + $time_taken" | bc)

      echo "Run $run: $procs processors, Time: $time_taken s"
    done

    # Compute the average execution time
    avg_time=$(echo "scale=4; $total_time / $REPEATS" | bc)
    echo "$procs,$avg_time" >>$output_file
  done
}

# Iterate over scaling types first, then problem sizes
for scaling in "strong" "weak"; do
  for size in "SMALL $SMALL" "MEDIUM $MEDIUM" "LARGE $LARGE"; do
    read -r size_desc num_points <<<"$size"
    run_experiment "$scaling" "$size_desc" "$num_points"
  done
done
