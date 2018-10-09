import socket
import sys
import getopt


def send(cmd, port=7002, ip="127.0.0.1"):
    if not cmd:
        raise ValueError("no command given!")

    adress = (ip, port)

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(adress)
    client.send(cmd.encode("ascii"))
    response = client.recv(1024)
    client.close()
    return str(response)


def main(argv):
    # backspace_pipe_commander.py -h (HELP)
    # backspace_pipe_commander.py -i 127.0.0.1 (IP)
    # backspace_pipe_commander.py -p 7002 (PORT)
    # backspace_pipe_commander.py -c apythoncommand (COMMANDSTRING)

    cmd = ''
    ip = '127.0.0.1'
    port = 7002
    helped = False

    try:
        opts, args = getopt.getopt(argv, "i:p:c:h")
    except getopt.GetoptError as e:
        print(e)
        print("usage: (-i) (-p) -c commandstring")
        return False

    for opt, arg in opts:
        if opt == '-h':
            print("usage: (-i) (-p) -c commandstring")
            helped = True
        elif opt == '-i':
            ip = arg
        elif opt == '-p':
            port = int(arg)
        elif opt == '-c':
            cmd = arg

    if not helped:
        print("send(cmd='{}',port={},ip='{}')".format(cmd, port, ip))
        response = send(cmd=cmd, port=port, ip=ip)
        print(response)


if __name__ == '__main__':
    main(sys.argv[1:])
