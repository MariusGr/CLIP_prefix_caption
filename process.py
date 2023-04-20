print("Loading CLIP, connecting to the process will fail till done loading...")
import socket
import sys
import predict
import struct
import _pickle as cPickle
print("CLIP loaded")

HOST = sys.argv[1]
PORT = int(sys.argv[2])
payload_size = struct.calcsize("I")

def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    print(f"CLIP TCP Server  Up: {HOST} {PORT}")
    sock.listen(1)

    while True:
        print('waiting for a connection')
        connection, client_address = sock.accept()
        try:
            print('connection from', client_address)
            data = b''
            while True:
                while len(data) < payload_size:
                    data += connection.recv(4096)

                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack("I", packed_msg_size)[0]

                while len(data) < msg_size:
                    data += connection.recv(4096)
                    
                frame_data = data[:msg_size]
                data = data[msg_size:]
                if frame_data == '':
                    break
                frame = cPickle.loads(frame_data)

                answer = predict.get_captions(frame)
                print('sending data back to the client')
                connection.sendall(answer.encode("utf-8"))
        finally:
            # Clean up the connection
            connection.close()
