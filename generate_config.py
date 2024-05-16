import os

# General
tester = "Axel"
config_dir = "test"

# Detailed
host_ip = "127.0.0.1"
if tester == "Axel":
    host_ip = "100.86.126.26"

client_ports = [5000, 5001, 5002]

client_names = ['A', 'B', 'C']

# function
def generate_config():
    for i in range(len(client_names)):
        with open(os.path.join("test", client_names[i]+".txt"), mode='w') as f:
            for j in range(len(client_names)):
                if i != j:
                    f.write(f"{host_ip}:{client_ports[j]}\n")

# main
if __name__ == "__main__":
    generate_config()