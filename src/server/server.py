import time, socket, os
HOST=""
PORT=49154

###CRYPTO LAYER###
KEY = 12
def CaesarEncrypt(data):
    result = ""
    for i in range(len(data)):
        char = data[i]
        if(char.isalpha()):
            if (char.isupper()):
                result += chr((ord(char) + KEY-65) % 26 + 65)
            else:
                result += chr((ord(char) + KEY - 97) % 26 + 97)
        else:
            result += char
  
    return result

def CaesarDecrypt(data):
    result = ""
    for i in range(len(data)):
        char = data[i]
        if(char.isalpha()):
            if(char.isupper()):
                result += chr((ord(char) - 65 + 26 - KEY) % 26 + 65)
            else:
                result += chr((ord(char) -97 + 26 - KEY) % 26 + 97)
        else:
            result+=char
    return result

def TransposeEncrypt(data):
    words = data.split()
    transposed_words = [word[::-1] for word in words]
    encrypted_data = " ".join(transposed_words)
    return encrypted_data

def TransposeDecrypt(data):
    return TransposeEncrypt(data)

def MyEncrypt(data,type = "caesar"):
    encrypted_data = ""
    header = ""
    if(type == "caesar"):
        header = "ca-"
        encrypted_data = CaesarEncrypt(data)
    elif(type == "transpose"):
        header = "tr-"
        encrypted_data = TransposeEncrypt(data)
    else:
        header = "pl-"
        encrypted_data = data
    return (header+encrypted_data).encode()

def MyDecrypt(data):
    decoded_data = data.decode()
    header = decoded_data[:3]
    encrypted_data = decoded_data[3:]
    decrypted_data = ""
    if(header == "ca-"):
        decrypted_data = CaesarDecrypt(encrypted_data)
    elif(header == "tr-"):
        decrypted_data = TransposeDecrypt(encrypted_data)
    elif(header == "pl-"):
        decrypted_data = encrypted_data
    return decrypted_data
###CRYPTO LAYER###

###SERVER SOCKET###
class ServerSoc:
    def __init__(self):
        self.soc = self.Create()
        self.host = None
        self.port = None
        self.curr_client_conn = None
        self.curr_client_ip = None
  
    def Create(self):
        try:
            soc = socket.socket()
            print("Socket Created at server end")
            return soc
        except socket.error as err:
            print("Socket creation error")

    def Listen(self,max_conn_wait_count):
        self.soc.listen(max_conn_wait_count)
        print("Listening At Port : " + str(self.port))

    def Bind(self,host,port):
        try:
            self.host = host
            self.port = port
            self.soc.bind((host,port)) 
            self.Listen(5)
        except socket.error as err:
            print("Socket binding error")
            self.Bind((host,port))

    def AcceptConn(self):
        self.curr_client_conn,address = self.soc.accept()
        self.curr_client_ip = address[0]
        print("Connection established with client IP= " + self.curr_client_ip + " | Port: " + str(self.port))

    def CloseConn(self):
        self.curr_client_conn.close()
        print("Connection closed with client IP= "+ self.curr_client_ip)

    def Close(self):
        self.soc.close()
        print("Closing the Server Socket")
###SERVER SOCKET###

def upload_to_client(conn,fileloc):
    header = "dwdr "
    conn.sendall(MyEncrypt(header))

    with open(fileloc, "rb") as file:
        while True:
            file_data = file.read()
            if not file_data:
                break
            conn.sendall(MyEncrypt(file_data.decode()))
    time.sleep(1)      
    footer = "dwdrend"
    conn.send(MyEncrypt(footer))

def download_from_client(conn,filename):
    with open(filename,"wb") as f:
        while(True):
            content = MyDecrypt(conn.recv(1024))
            if "updrend" in content:
                break
            else:
                f.write(content.encode())

def Interaction(s):
    while(True):
        client_conn = s.curr_client_conn
        data = MyDecrypt(client_conn.recv(1024))
        data_to_be_sent = ""
        header = ""
        if(data == "QUIT"):
            s.CloseConn()
            break
        if(data[:2] == "CD"):
            header = "cdr "
            try:
                os.chdir(data[3:])
                data_to_be_sent += "STATUS: OK"
            except:
                data_to_be_sent += "STATUS: NOK" 
        elif(data[:3] == "CWD"):
            header = "cwdr " 
            data_to_be_sent += os.getcwd()
        elif(data[:2] == "LS"):
            header = "lsr "
            path = os.getcwd()
            file_dirs = os.listdir(path)
            for file_dir_name in file_dirs:
                data_to_be_sent += file_dir_name
                data_to_be_sent += " "
            data_to_be_sent = data_to_be_sent[:len(data_to_be_sent)-1]

        if(len(data_to_be_sent)!=0):
            data_to_be_sent = header + data_to_be_sent
            data_to_be_sent = MyEncrypt(data_to_be_sent)
            client_conn.send(data_to_be_sent)

        if(data[:3] == "DWD"):
            fileloc = data[4:]
            try:
                upload_to_client(client_conn,fileloc)
                time.sleep(1)
                data_to_be_sent += "fdwd STATUS: OK"
            except:
                data_to_be_sent += "fdwd STATUS: NOK"
            data_to_be_sent = MyEncrypt(data_to_be_sent)
            client_conn.send(data_to_be_sent)

        if(data[:3] == "UPD"):
            filename = data[4:]
            try:
                download_from_client(client_conn,filename)
                time.sleep(1)
                data_to_be_sent += "fupd STATUS:OK"
            except:
                data_to_be_sent += "fupd STATUS: NOK"
            data_to_be_sent = MyEncrypt(data_to_be_sent)
            client_conn.send(data_to_be_sent)

def main():
    s = ServerSoc()
    s.Bind(HOST,PORT)
    while(True):
        s.AcceptConn()
        Interaction(s)
        

if(__name__ == "__main__"):
    main()
