#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>

int main(int argc, char *argv[]) {
    MPI_Init(&argc, &argv);  // Initialize the MPI environment

    if (argc != 2) {
        fprintf(stderr, "Usage: %s <number_of_points>\n", argv[0]);
        MPI_Finalize();
        return 1;
    }

    long long int num_points = atoll(argv[1]);
    long long int in_circle = 0;
    double x, y;

    srand(time(NULL));  // Initialize random seed

    // Starting the timer
    double start_time = MPI_Wtime();

    // Perform the Monte Carlo simulation
    for (long long int i = 0; i < num_points; i++) {
        x = (double)rand() / RAND_MAX;  // Random x from 0 to 1
        y = (double)rand() / RAND_MAX;  // Random y from 0 to 1
        if (x * x + y * y <= 1) in_circle++;
    }

    double end_time = MPI_Wtime();

    double pi_estimate = 4 * (double)in_circle / num_points;
    printf("Estimated Pi = %f\n", pi_estimate);
    printf("Time taken = %f seconds\n", end_time - start_time);

    MPI_Finalize();  // Finalize the MPI environment
    return 0;
}
