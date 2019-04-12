import socket
import sys
 
HOST = ''  # Symbolic name meaning all available interfaces
PORT = 8888 # Arbitrary non-privileged port
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'Socket created'

try:
    s.bind((HOST, PORT))
except socket.error as e:
    print 'Bind failed.Error code: ',e
    sys.exit()          
print 'Socket bind complete'
s.listen(10)
print 'Socket now listening'
#wait to accept a connection - blocking call
conn, addr = s.accept()
 
 #display client information
print 'Connected with ',addr[0],':',str(addr[1])
#now keep talking with the client
data = conn.recv(1024)
conn.sendall(data)
 
conn.close()
s.close()
