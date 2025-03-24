#include <stdio.h>
#include <stdlib.h>
#include <mpi.h>

int main(int argc, char *argv[]) {
    MPI_Init(&argc, &argv);

    int rank;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);

    const int N = 1000;  // Number of ping-pong iterations
    const int message_size = 1024;  // Size of each message in bytes

    // Allocate message buffer
    char *message = (char *)malloc(message_size);
    if (message == NULL) {
        fprintf(stderr, "Failed to allocate message buffer.\n");
        MPI_Abort(MPI_COMM_WORLD, EXIT_FAILURE);
        exit(EXIT_FAILURE);
    }

    double start_time, end_time;
    MPI_Status status;

    // Buffer for buffered send
    int bsize = message_size + MPI_BSEND_OVERHEAD;
    char *buffer = (char *)malloc(bsize);
    if (buffer == NULL) {
        free(message);
        fprintf(stderr, "Failed to allocate buffer for MPI_Bsend.\n");
        MPI_Abort(MPI_COMM_WORLD, EXIT_FAILURE);
        exit(EXIT_FAILURE);
    }
    MPI_Buffer_attach(buffer, bsize);

    // Synchronize before starting timing
    MPI_Barrier(MPI_COMM_WORLD);

    // Standard Send-Recv communication
    start_time = MPI_Wtime();
    for (int i = 0; i < N; i++) {
        if (rank == 0) {
            MPI_Send(message, message_size, MPI_CHAR, 1, 0, MPI_COMM_WORLD);
            MPI_Recv(message, message_size, MPI_CHAR, 1, 0, MPI_COMM_WORLD, &status);
        } else {
            MPI_Recv(message, message_size, MPI_CHAR, 0, 0, MPI_COMM_WORLD, &status);
            MPI_Send(message, message_size, MPI_CHAR, 0, 0, MPI_COMM_WORLD);
        }
    }
    end_time = MPI_Wtime();
    double elapsed_standard = (end_time - start_time) / (2 * N);

    // Reset Barrier before starting buffered communication
    MPI_Barrier(MPI_COMM_WORLD);

    // Buffered Send-Recv communication
    start_time = MPI_Wtime();
    for (int i = 0; i < N; i++) {
        if (rank == 0) {
            MPI_Bsend(message, message_size, MPI_CHAR, 1, 0, MPI_COMM_WORLD);
            MPI_Recv(message, message_size, MPI_CHAR, 1, 0, MPI_COMM_WORLD, &status);
        } else {
            MPI_Recv(message, message_size, MPI_CHAR, 0, 0, MPI_COMM_WORLD, &status);
            MPI_Bsend(message, message_size, MPI_CHAR, 0, 0, MPI_COMM_WORLD);
        }
    }
    end_time = MPI_Wtime();
    double elapsed_buffered = (end_time - start_time) / (2 * N);

    // Detach the buffer
    MPI_Buffer_detach(&buffer, &bsize);

    if (rank == 0) {
        printf("Average Round-Trip Time (Standard): %f ms\n", elapsed_standard * 1000);
        printf("Average Round-Trip Time (Buffered): %f ms\n", elapsed_buffered * 1000);
    }

    free(message);
    free(buffer);
    MPI_Finalize();
    return 0;
}
