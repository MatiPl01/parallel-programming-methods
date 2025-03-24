#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>

int main(int argc, char *argv[]) {
    MPI_Init(&argc, &argv);

    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    if (argc != 2) {
        if (rank == 0) {
            fprintf(stderr, "Usage: %s <number_of_points>\n", argv[0]);
        }
        MPI_Finalize();
        return 1;
    }

    long long int points_per_process = atoll(argv[1]) / size;
    long long int count_in_circle = 0, total_in_circle;

    srand(time(NULL) + rank);  // Different seed for each process

    // Synchronization before starting the timing
    MPI_Barrier(MPI_COMM_WORLD);
    double start_time = MPI_Wtime();

    // Perform the Monte Carlo simulation in parallel
    for (long long int i = 0; i < points_per_process; i++) {
        double x = (double)rand() / RAND_MAX;
        double y = (double)rand() / RAND_MAX;
        if (x * x + y * y <= 1) {
            count_in_circle++;
        }
    }

    // Collects all partial counts in the root process
    MPI_Reduce(&count_in_circle, &total_in_circle, 1, MPI_LONG_LONG_INT, MPI_SUM, 0, MPI_COMM_WORLD);
    
    // Synchronization to ensure all processes finish before stopping the timing
    MPI_Barrier(MPI_COMM_WORLD);
    double end_time = MPI_Wtime();

    if (rank == 0) {
        double pi_estimate = 4 * (double)total_in_circle / (points_per_process * size);
        printf("Estimated Pi = %f\n", pi_estimate);
        printf("Time taken = %f seconds\n", end_time - start_time);
    }

    MPI_Finalize();
    return 0;
}
