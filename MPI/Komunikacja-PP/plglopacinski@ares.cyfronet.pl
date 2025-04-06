#include <stdio.h>
#include <stdlib.h>
#include <mpi.h>

int main(int argc, char *argv[]) {
    int rank, size, data_to_send, data_received;
    MPI_Status status;
    MPI_Request request;

    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    if (size != 2) {
        fprintf(stderr, "This program requires exactly two MPI processes.\n");
        MPI_Abort(MPI_COMM_WORLD, 1);
    }

    data_to_send = 7;

    if (rank == 0) {
        // Standard send
        MPI_Send(&data_to_send, 1, MPI_INT, 1, 0, MPI_COMM_WORLD);
        MPI_Recv(&data_received, 1, MPI_INT, 1, 1, MPI_COMM_WORLD, &status);
        printf("Standard Send-Recv: %d\n", data_received);

        // Synchronous send
        MPI_Ssend(&data_to_send, 1, MPI_INT, 1, 2, MPI_COMM_WORLD);
        MPI_Recv(&data_received, 1, MPI_INT, 1, 3, MPI_COMM_WORLD, &status);
        printf("Synchronous Send-Recv: %d\n", data_received);

        // Buffered send
        int bufsize = MPI_BSEND_OVERHEAD + sizeof(int);
        char* buffer = (char*) malloc(bufsize);
        MPI_Buffer_attach(buffer, bufsize);
        MPI_Bsend(&data_to_send, 1, MPI_INT, 1, 4, MPI_COMM_WORLD);
        MPI_Recv(&data_received, 1, MPI_INT, 1, 5, MPI_COMM_WORLD, &status);
        printf("Buffered Send-Recv: %d\n", data_received);
        MPI_Buffer_detach(&buffer, &bufsize);
        free(buffer);

        // Ready send
        MPI_Rsend(&data_to_send, 1, MPI_INT, 1, 6, MPI_COMM_WORLD);
        MPI_Recv(&data_received, 1, MPI_INT, 1, 7, MPI_COMM_WORLD, &status);
        printf("Ready Send-Recv: %d\n", data_received);

        // Non-blocking send
        MPI_Isend(&data_to_send, 1, MPI_INT, 1, 8, MPI_COMM_WORLD, &request);
        MPI_Wait(&request, &status);
        MPI_Recv(&data_received, 1, MPI_INT, 1, 9, MPI_COMM_WORLD, &status);
        printf("Non-blocking Send-Recv: %d\n", data_received);
    } else if (rank == 1) {
        MPI_Recv(&data_received, 1, MPI_INT, 0, 0, MPI_COMM_WORLD, &status);
        MPI_Send(&data_received, 1, MPI_INT, 0, 1, MPI_COMM_WORLD);
        
        MPI_Recv(&data_received, 1, MPI_INT, 0, 2, MPI_COMM_WORLD, &status);
        MPI_Ssend(&data_received, 1, MPI_INT, 0, 3, MPI_COMM_WORLD);
        
        MPI_Recv(&data_received, 1, MPI_INT, 0, 4, MPI_COMM_WORLD, &status);
        MPI_Send(&data_received, 1, MPI_INT, 0, 5, MPI_COMM_WORLD);
        
        MPI_Recv(&data_received, 1, MPI_INT, 0, 6, MPI_COMM_WORLD, &status);
        MPI_Send(&data_received, 1, MPI_INT, 0, 7, MPI_COMM_WORLD);
        
        MPI_Recv(&data_received, 1, MPI_INT, 0, 8, MPI_COMM_WORLD, &status);
        MPI_Isend(&data_received, 1, MPI_INT, 0, 9, MPI_COMM_WORLD, &request);
        MPI_Wait(&request, &status);
    }

    MPI_Finalize();
    return 0;
}
