#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>

#define MAX_MSG_SIZE 1048576  // Maximum message size: 1MB
#define REPETITIONS 1000      // Number of repetitions for each message size

int main(int argc, char* argv[]) {
    MPI_Init(&argc, &argv);
    
    int rank, num_reps = REPETITIONS;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    
    if (argc > 1) {
        num_reps = atoi(argv[1]);
        if (num_reps <= 0) {
            if (rank == 0) {
                fprintf(stderr, "Number of repetitions must be a positive integer\n");
            }
            MPI_Abort(MPI_COMM_WORLD, EXIT_FAILURE);
        }
    }

    double start_time, end_time;
    char *buffer = malloc(MAX_MSG_SIZE);
    if (buffer == NULL) {
        fprintf(stderr, "Failed to allocate buffer of size %d.\n", MAX_MSG_SIZE);
        MPI_Abort(MPI_COMM_WORLD, EXIT_FAILURE);
    }
    MPI_Status status;

    // Prepare buffer for MPI_Bsend
    int bsize = MAX_MSG_SIZE + MPI_BSEND_OVERHEAD;
    char *bsend_buffer = malloc(bsize);
    if (bsend_buffer == NULL) {
        free(buffer);
        fprintf(stderr, "Failed to allocate buffer for MPI_Bsend.\n");
        MPI_Abort(MPI_COMM_WORLD, EXIT_FAILURE);
    }
    MPI_Buffer_attach(bsend_buffer, bsize);
    
    // Testing different message sizes
    for (int size = 1; size <= MAX_MSG_SIZE; size *= 2) {
        // Standard Send-Recv for throughput and delay
        MPI_Barrier(MPI_COMM_WORLD);  // Synchronize before each test
        start_time = MPI_Wtime();
        for (int i = 0; i < num_reps; i++) {
            if (rank == 0) {
                MPI_Send(buffer, size, MPI_CHAR, 1, 0, MPI_COMM_WORLD);
                MPI_Recv(buffer, size, MPI_CHAR, 1, 0, MPI_COMM_WORLD, &status);
            } else {
                MPI_Recv(buffer, size, MPI_CHAR, 0, 0, MPI_COMM_WORLD, &status);
                MPI_Send(buffer, size, MPI_CHAR, 0, 0, MPI_COMM_WORLD);
            }
        }
        end_time = MPI_Wtime();

        double elapsed = (end_time - start_time) / (2.0 * num_reps); // Total for num_reps round-trips
        double throughput = (size * 8.0 / elapsed) / 1e6; // Convert to Mbps

        if (rank == 0) {
            if (size == 1) {
                // Special case for delay measurement
                printf("Delay for 1 byte: %f ms\n", elapsed * 1000);
            }
            printf("Standard Communication: Size %d bytes, Throughput: %f Mbps\n", size, throughput);
        }
        
        // Reset Barrier and repeat for Buffered Send-Recv
        MPI_Barrier(MPI_COMM_WORLD);
        start_time = MPI_Wtime();
        for (int i = 0; i < num_reps; i++) {
            if (rank == 0) {
                MPI_Bsend(buffer, size, MPI_CHAR, 1, 0, MPI_COMM_WORLD);
                MPI_Recv(buffer, size, MPI_CHAR, 1, 0, MPI_COMM_WORLD, &status);
            } else {
                MPI_Recv(buffer, size, MPI_CHAR, 0, 0, MPI_COMM_WORLD, &status);
                MPI_Bsend(buffer, size, MPI_CHAR, 0, 0, MPI_COMM_WORLD);
            }
        }
        end_time = MPI_Wtime();

        elapsed = (end_time - start_time) / (2.0 * num_reps);
        throughput = (size * 8.0 / elapsed) / 1e6;
        
        if (rank == 0) {
            printf("Buffered Communication: Size %d bytes, Throughput: %f Mbps\n", size, throughput);
        }
    }

    MPI_Buffer_detach(&bsend_buffer, &bsize);
    free(bsend_buffer);
    free(buffer);
    MPI_Finalize();
    return 0;
}
