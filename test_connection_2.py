import socket
sock = socket.socket()
sock.settimeout(5)
try:
    sock.connect(("34.81.63.188", 5432))
    print("✅ 可以連上 5432 port")
except Exception as e:
    print("❌ 連線失敗：", e)
finally:
    sock.close()
