import socket
import os
import time
SERVER_IP = "127.0.0.1"
SERVER_PORT = 49154

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

def download_from_server(soc,filename):
    with open(filename,"wb") as f:
        while(True):
            content = MyDecrypt(soc.recv(1024))
            if "dwdrend" in content:
                break
            else:
                f.write(content.encode())

    while(True):
        response = MyDecrypt(soc.recv(1024))
        if(response[:4] == "fdwd"):
            print(response[5:])
            break

def upload_to_server(soc,filename):
    with open(filename, "rb") as file:
        while True:
            file_data = file.read()
            if not file_data:
                break
            soc.sendall(MyEncrypt(file_data.decode()))
    time.sleep(1)      
    footer = "updrend"
    soc.send(MyEncrypt(footer))

    while(True):
        response = MyDecrypt(soc.recv(1024))
        if(response[:4] == "fupd"):
            print(response[5:])
            break 

def Interaction(soc):
    while(True):
        cmd = input()
        encrypted_cmd = MyEncrypt(cmd)
          
        if(len(cmd)>0):
            soc.send(encrypted_cmd)
            if(cmd == "QUIT"):
                soc.close()
                print("Closing connection with server IP: "+ SERVER_IP)
                break 
            if(cmd[:3] == "UPD"):
                filename = cmd[4:]
                upload_to_server(soc,filename)
                continue
            to_be_printed = ""
            response = MyDecrypt(soc.recv(1024))
            if(response[:3] == "cdr"):
                to_be_printed += response[4:]
            if(response[:4] == "cwdr"):
                cwd = response[5:]
                to_be_printed += cwd
            elif(response[:3] == "lsr"):
                ls = response[4:]
                to_be_printed += ls
            elif(response[:4] == "dwdr"):
                filename = cmd.split()[1]
                download_from_server(soc,filename)
            if(len(to_be_printed)!=0):
                print(to_be_printed)


def main():
    soc = socket.socket()
    print("Socket Created at client end")

    try:
        soc.connect((SERVER_IP,SERVER_PORT))
        print("Connnected to Server IP= "+ SERVER_IP)
    except socket.error:
        print("Attempt failed for connection with Server IP= "+SERVER_IP)
        return
    
    Interaction(soc)


if(__name__ == "__main__"):
    main()
