import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

# Tworzenie katalogu na wykresy, jeśli nie istnieje
output_dir = "out"
os.makedirs(output_dir, exist_ok=True)

# Wczytywanie danych dla skalowania silnego
strong_small = pd.read_csv("results_strong_scaling_SMALL.csv")
strong_medium = pd.read_csv("results_strong_scaling_MEDIUM.csv")
strong_large = pd.read_csv("results_strong_scaling_LARGE.csv")

# Wczytywanie danych dla skalowania słabego
weak_small = pd.read_csv("results_weak_scaling_SMALL.csv")
weak_medium = pd.read_csv("results_weak_scaling_MEDIUM.csv")
weak_large = pd.read_csv("results_weak_scaling_LARGE.csv")

# Przypisanie etykiet i kolorów do wykresów
dataset_labels = ["Mały problem", "Średni problem", "Duży problem"]
colors = ["blue", "green", "red"]

# Funkcja do rysowania wykresów ogólnych (np. czas wykonania)
def plot_scaling_metric(title, ylabel, filename, datasets, metric_func=None):
    plt.figure(figsize=(10, 6))

    # Iteracja po rozmiarach problemu i przetwarzanie danych
    for data, label, color in zip(datasets, dataset_labels, colors):
        metric_values = metric_func(data) if metric_func else data["Time (s)"]
        plt.plot(data["Processors"], metric_values, 'o-', label=label, color=color)

    plt.xlabel("Liczba procesorów")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.grid()
    plt.savefig(f"{output_dir}/{filename}")
    plt.show()

# Funkcja do rysowania wykresu przyspieszenia z linią idealnego skalowania (y = x)
def plot_speedup(title, filename, datasets):
    plt.figure(figsize=(10, 6))

    # Pobieranie liczby procesorów dla wyznaczenia linii idealnego skalowania
    processors = np.array(strong_small["Processors"])
    plt.plot(processors, processors, 'k--', label="Idealne skalowanie", alpha=0.7)

    # Iteracja po rozmiarach problemu i obliczanie przyspieszenia
    for data, label, color in zip(datasets, dataset_labels, colors):
        speedup = data["Time (s)"].iloc[0] / data["Time (s)"]
        plt.plot(data["Processors"], speedup, 'o-', label=label, color=color)

    plt.xlabel("Liczba procesorów")
    plt.ylabel("Przyspieszenie")
    plt.title(title)
    plt.legend()
    plt.grid()
    plt.savefig(f"{output_dir}/{filename}")
    plt.show()

# Funkcja do rysowania wykresu efektywności z linią y = 1 (idealna efektywność)
def plot_efficiency(title, filename, datasets):
    plt.figure(figsize=(10, 6))

    # Dodanie poziomej linii efektywności = 1
    plt.axhline(y=1, color='k', linestyle='--', label="Idealna efektywność")

    # Iteracja po rozmiarach problemu i obliczanie efektywności
    for data, label, color in zip(datasets, dataset_labels, colors):
        speedup = data["Time (s)"].iloc[0] / data["Time (s)"]
        efficiency = speedup / data["Processors"]
        plt.plot(data["Processors"], efficiency, 'o-', label=label, color=color)

    plt.xlabel("Liczba procesorów")
    plt.ylabel("Efektywność (Speedup / P)")
    plt.title(title)
    plt.legend()
    plt.grid()
    plt.savefig(f"{output_dir}/{filename}")
    plt.show()

# Funkcja do rysowania wykresu części sekwencyjnej (prawa Amdahla)
def plot_serial_fraction(title, filename, datasets):
    plt.figure(figsize=(10, 6))

    # Iteracja po rozmiarach problemu i obliczanie części sekwencyjnej
    for data, label, color in zip(datasets, dataset_labels, colors):
        speedup = data["Time (s)"].iloc[0] / data["Time (s)"]
        serial_fraction = (1 / speedup - 1 / data["Processors"]) / (1 - 1 / data["Processors"])
        plt.plot(data["Processors"], serial_fraction, 'o-', label=label, color=color)

    plt.xlabel("Liczba procesorów")
    plt.ylabel("Część sekwencyjna")
    plt.title(title)
    plt.legend()
    plt.grid()
    plt.savefig(f"{output_dir}/{filename}")
    plt.show()

# Silne skalowanie
plot_scaling_metric(
    title="Czas wykonania w zależności od liczby procesorów (Skalowanie silne)",
    ylabel="Czas wykonania (s)",
    filename="time_vs_processors_strong.png",
    datasets=[strong_small, strong_medium, strong_large]
)

plot_speedup(
    title="Przyspieszenie w zależności od liczby procesorów (Skalowanie silne)",
    filename="speedup_vs_processors_strong.png",
    datasets=[strong_small, strong_medium, strong_large]
)

plot_efficiency(
    title="Efektywność w zależności od liczby procesorów (Skalowanie silne)",
    filename="efficiency_vs_processors_strong.png",
    datasets=[strong_small, strong_medium, strong_large]
)

plot_serial_fraction(
    title="Część sekwencyjna w zależności od liczby procesorów (Skalowanie silne)",
    filename="serial_fraction_vs_processors_strong.png",
    datasets=[strong_small, strong_medium, strong_large]
)

# Słabe skalowanie
plot_scaling_metric(
    title="Czas wykonania w zależności od liczby procesorów (Skalowanie słabe)",
    ylabel="Czas wykonania (s)",
    filename="time_vs_processors_weak.png",
    datasets=[weak_small, weak_medium, weak_large]
)

plot_speedup(
    title="Przyspieszenie w zależności od liczby procesorów (Skalowanie słabe)",
    filename="speedup_vs_processors_weak.png",
    datasets=[weak_small, weak_medium, weak_large]
)

plot_efficiency(
    title="Efektywność w zależności od liczby procesorów (Skalowanie słabe)",
    filename="efficiency_vs_processors_weak.png",
    datasets=[weak_small, weak_medium, weak_large]
)

plot_serial_fraction(
    title="Część sekwencyjna w zależności od liczby procesorów (Skalowanie słabe)",
    filename="serial_fraction_vs_processors_weak.png",
    datasets=[weak_small, weak_medium, weak_large]
)