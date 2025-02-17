import socket

host = ''  # Server IP or Hostname
port = 8005  # Pick an open Port (1000+ recommended), must match the client port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Socket created")

# Managing error exception
try:
    s.bind((host, port))
except socket.error as msg:
    print(msg)
    print("Bind failed")

s.listen(5)
print("Socket awaiting messages")
(conn, addr) = s.accept()
print("Connected")

# Awaiting for message
while True:
    data = conn.recv(1024)
    data = data.decode('utf-8')

    reply = ''
    print(data)

    reply = "Number of cars sent to server"
    conn.send(str.encode(reply))

conn.close()  # Close connections