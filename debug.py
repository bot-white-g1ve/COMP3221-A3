from datetime import datetime

port = 0

def d_print(func, str):
    with open(f'debug_for_{port}.txt', 'a') as f:
        f.write(f"(In {func}) {str}\n")
    pass

def d_initial(port_from_program):
    global port
    port = port_from_program
    with open(f'debug_for_{port}.txt', 'a') as f:
        f.write("\n")
    d_print("initializing", datetime.now())
    d_print("initializing", f"bind to port {port}")
    pass

if __name__ == '__main__':
    d_initial('debug_test')
    d_print("testing", "testing")