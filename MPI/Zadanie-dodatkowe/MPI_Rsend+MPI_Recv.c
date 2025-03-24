/*
Dlaczego działa:
MPI_Rsend (Ready Send) to funkcja wysyłająca w MPI, która wymaga upewnienia się, że odbiorca już zainicjował operację odbioru (MPI_Recv) przed rozpoczęciem tego wysyłania. Dzięki temu, MPI_Rsend jest w stanie wysłać dane bez dodatkowej synchronizacji i z mniejszym narzutem, ponieważ zakłada gotowość odbiorcy.

W naszym przypadku, uruchamiamy MPI_Recv na procesie o ranku 1 przed wykonaniem MPI_Rsend na procesie o ranku 0, co spełnia wymagania MPI_Rsend dla prawidłowego wykonania. Dzięki temu zabiegowi unikamy potencjalnego zakleszczenia, które mogłoby wystąpić, gdyby nadawca próbował wysłać dane przed inicjowaniem operacji odbioru przez odbiorcę.
*/

#include <mpi.h>
#include <stdio.h>

int main(int argc, char **argv) {
    MPI_Init(&argc, &argv);

    int world_rank;
    MPI_Comm_rank(MPI_COMM_WORLD, &world_rank);
    
    int data = -1; // Zmienna przechowująca dane do wysłania/odbioru

    // Proces o ranku 0 pełni rolę nadawcy.
    if (world_rank == 0) {
        data = 100;  // Przygotowanie danych do wysłania.
        // Użycie MPI_Rsend dla wysłania danych.
        MPI_Rsend(&data, 1, MPI_INT, 1, 0, MPI_COMM_WORLD);
    }
    // Proces o ranku 1 pełni rolę odbiorcy.
    else if (world_rank == 1) {
        // Użycie MPI_Recv dla odbioru danych.
        // MPI_Recv jest funkcją blokującą i czeka, aż dane będą gotowe do odbioru.
        MPI_Recv(&data, 1, MPI_INT, 0, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        // Wypisanie odebranych danych.
        printf("Received %d\n", data);
    }

    // Finalizacja środowiska MPI.
    MPI_Finalize();
    return 0;
}
