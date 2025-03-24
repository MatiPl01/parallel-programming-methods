import re

# Setup the input and output file names
input_filename = './in/raw_data.txt'
output_filename = './out/data.csv'

# Regex patterns to match lines
delay_pattern = re.compile(r'^Delay for 1 byte: ([\d\.]+) ms$')
throughput_pattern = re.compile(r'^(Standard|Buffered) Communication: Size (\d+) bytes, Throughput: ([\d\.]+) Mbps$')

# Data structure to hold the parsed data
data = {'Size': [], 'Standard_Throughput': [], 'Buffered_Throughput': [], 'Delay': None}

# Read & Process the input file
with open(input_filename, 'r') as file:
    for line in file:
        line = line.strip()
        if delay_match := delay_pattern.match(line):
            data['Delay'] = float(delay_match.group(1))
        elif throughput_match := throughput_pattern.match(line):
            comm_type = throughput_match.group(1)
            size = int(throughput_match.group(2))
            throughput = float(throughput_match.group(3))

            if comm_type == 'Standard':
                if size not in data['Size']:
                    data['Size'].append(size)
                    data['Standard_Throughput'].append(throughput)
                    data['Buffered_Throughput'].append(None)  # Placeholder until buffered value is found
            else:  # Buffered
                index = data['Size'].index(size)
                data['Buffered_Throughput'][index] = throughput

# Write the processed data to CSV
with open(output_filename, 'w') as file:
    header = 'Size,Standard_Throughput,Buffered_Throughput\n'
    file.write(header)
    for size, sth, bth in zip(data['Size'], data['Standard_Throughput'], data['Buffered_Throughput']):
        line = f'{size},{sth},{bth}\n'
        file.write(line)

# Optionally print out the delay
print(f"Delay for 1 byte: {data['Delay']} ms")
