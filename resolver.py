import socket
import sys
import random
import struct
import io

class Header:
    def __init__(self, id, flags):
        self.id = id
        # from the demo code
        self.response_code = flags & 0b00001111
        self.is_authoritative = bool(flags & 0b00010000)
        self.is_truncated = bool(flags & 0b00100000)
        self.is_recursion_desired = bool(flags & 0b10000000)
        self.is_recursion_available = bool(flags & 0b01000000)

    def __repr__(self):
        return f'<Id:{self.id} Response Code:{self.response_code} Authoritative:{self.is_authoritative} Truncated:{self.is_truncated} Recursion Desired:{self.is_recursion_desired} Available:{self.is_recursion_available}>'

class Record:
    def __init__(self, name, type, ans):
        self.name = name
        if type == 1:
            self.type = 'A'
        elif type == 2:
            self.type = 'NS'
        elif type == 5:
            self.type = 'CNAME'
        # not supporting other types yet
        else:
            self.type = type
        self.ans = ans

    def __repr__(self):
        return f'<Name:{self.name} Type:{self.type} Answer:{self.ans}>'

def load_root():
    # get ip address of each root in A record only
    root_ip = []
    try:
        # look into named.root file in the directory
        with open('named.root', 'r') as file:
            for line in file:
                line = line.strip()
                # ignore a line starting with ;
                if line and not line.startswith(';'):
                    parts = line.split()
                    if parts[2] == 'A':
                        # get ip address of root domain
                        root_ip.append(parts[3])
    except FileNotFoundError:
        print('Error: no named.root files')
    
    # return a list of roots' ip
    print('Successfully downloaded all roots ip')
    return root_ip
    
def start_server(port):

    root_ip = load_root()
    host = '127.0.0.1'

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))

    server_socket.listen(1)
    print('Server is listening on port', port)

    # continue receiving queries from clients
    while True:
        conn, address = server_socket.accept()
        print('Connection from', address)
        query = conn.recv(1024)
        if len(query) == 0:
            print("Error: invalid query")
            conn.close()
            continue

        # decode question
        _, questions, _, _, _ = decode(query)
        question_name = ''
        for record in questions:
            if record.type == 'A':
                question_name = record.name
        if len(question_name) == 0:
            print("Error: invalid query")
            conn.close()
            continue

        try:
            # start by asking from the roots
            # if one isn't getting back the answer, try the next one until the answer is returned or never
            ip_a = ''
            for ip in root_ip:
                print('start from root: ' + ip)
                response, ip_a = get_answer(ip, question_name, ip)
                if (len(ip_a) != 0):
                    conn.send(response)
                    break
            if (len(ip_a) == 0):
                print("Error: server can't find ", question_name)
        except KeyboardInterrupt:
            print('stop searching')
            conn.close()
            break
        print('----------------------------------------------')
        conn.close()

if __name__ == '__main__':
    # check for invalid arguments
    if len(sys.argv) != 2:
        print('Error: invalid arguments')
        print('Usage: resolver port')
        exit(1)

    server_port = int (sys.argv[1])
    if server_port < 1024 or server_port > 65535:
        print('Error: invalid arguments')
        print('Usage: resolver port')
        exit(1)

    # start the server
    try:
        start_server(server_port)
    except KeyboardInterrupt:
        print("stop the server")
    except Exception as E:
        print(f"Error: {E}:{E.args}")
