import pandas as pd
import matplotlib.pyplot as plt

# Wczytanie danych dla wewnątrzwęzłowej komunikacji
data_intra = pd.read_csv('./out/intra_node_data.csv')
# Wczytanie danych dla międzywęzłowej komunikacji
data_inter = pd.read_csv('./out/inter_node_data.csv')

# Tworzenie wykresu przepustowości dla komunikacji wewnątrzwęzłowej
plt.figure(figsize=(10, 5))
plt.plot(data_intra['Size'], data_intra['Standard_Throughput'], label='Komunikacja standardowa', marker='o')
plt.plot(data_intra['Size'], data_intra['Buffered_Throughput'], label='Komunikacja buforowana', marker='o')
plt.xscale('log', base=2)
plt.yscale('log', base=10)
plt.xlabel('Rozmiar wiadomości (bajty)')
plt.ylabel('Przepustowość (Mbps)')
plt.title('Przepustowość komunikacji wewnątrzwęzłowej MPI')
plt.legend()
plt.grid(True)
plt.savefig('./out/throughput_intra_node.png')
plt.show()

# Tworzenie wykresu przepustowości dla komunikacji międzywęzłowej
plt.figure(figsize=(10, 5))
plt.plot(data_inter['Size'], data_inter['Standard_Throughput'], label='Komunikacja standardowa', marker='o')
plt.plot(data_inter['Size'], data_inter['Buffered_Throughput'], label='Komunikacja buforowana', marker='o')
plt.xscale('log', base=2)
plt.yscale('log', base=10)
plt.xlabel('Rozmiar wiadomości (bajty)')
plt.ylabel('Przepustowość (Mbps)')
plt.title('Przepustowość międzywęzłowej komunikacji MPI')
plt.legend()
plt.grid(True)
plt.savefig('./out/throughput_inter_node.png')
plt.show()

# Wykresy opóźnień dla obu konfiguracji (jeśli masz takie dane)
delay_data = {
    'Configuracja': ['Wewnątrzwęzłowa', 'Międzywęzłowa'],
    'Opóźnienie_ms': [0.000444, 0.027149]
}
delay_df = pd.DataFrame(delay_data)

plt.figure(figsize=(6, 4))
plt.bar(delay_df['Configuracja'], delay_df['Opóźnienie_ms'], color=['blue', 'red'])
plt.xlabel('Konfiguracja')
plt.ylabel('Opóźnienie (ms)')
plt.title('Opóźnienia dla komunikacji MPI (1 bajt)')
plt.savefig('./out/delay_comparison.png')
plt.show()
