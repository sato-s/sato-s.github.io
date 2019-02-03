import sys, os, time, socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
hostName = socket.gethostbyname('www.google.ca')
print(hostName)
s.connect((hostName, 80))
s.send(b"GET / HTTP/1.0\r\n\r\n\r\n")
print (s.recv(500000000))
s.close
