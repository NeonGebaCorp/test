import socket
import subprocess
import random
import string
import requests
import os

SERVER_1_URL = 'https://nzst.xyz'
PORT = 5555

def generate_random_password(length=16):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for i in range(length))

def create_docker_container():
    password = generate_random_password()
    random_port = random.randint(2000, 65535)

    dockerfile_content = f"""
    FROM ubuntu:22.04

    RUN apt-get update && \\
        apt-get install -y openssh-server sudo && \\
        mkdir /var/run/sshd && \\
        echo 'root:{password}' | chpasswd && \\
        sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \\
        echo 'AllowUsers root' >> /etc/ssh/sshd_config && \\
        mkdir /root/.ssh && \\
        chmod 700 /root/.ssh && \\
        touch /root/.ssh/authorized_keys && \\
        chmod 600 /root/.ssh/authorized_keys

    EXPOSE 22

    CMD ["/usr/sbin/sshd", "-D"]
    """

    with open("Dockerfile", "w") as dockerfile:
        dockerfile.write(dockerfile_content)

    os.system("docker build -t my_vps_image .")
    os.system(f"docker run -d -p {random_port}:22 --name my_vps my_vps_image")

    container_id = subprocess.getoutput("docker ps -q -l")
    return password, random_port, container_id

def check_storage():
    total, used, free = shutil.disk_usage("/")
    used_percent = (used / total) * 100
    return used_percent

def handle_request(client_socket):
    request = client_socket.recv(1024).decode('utf-8')
    request_line = request.split('\n')[0]
    method, path, _ = request_line.split()

    if path.startswith('/servers'):
        if 'type=add' in path:
            if check_storage() >= 70:
                response = "VPS creation is disabled due to high storage usage."
            else:
                password, random_port, _ = create_docker_container()
                response = (f"Hostname: {socket.gethostname()}\n"
                            f"IP Address: {subprocess.getoutput('curl -s ifconfig.io')}\n"
                            f"Username: root\nPassword: {password}\nPort: {random_port}")
                requests.post(SERVER_1_URL, data={'response': response})
        else:
            response = "Invalid request type."
    else:
        response = "Not Found"

    client_socket.sendall(f"HTTP/1.1 200 OK\nContent-Type: text/plain\n\n{response}".encode('utf-8'))
    client_socket.close()

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', PORT))
    server_socket.listen(5)
    print(f"Server listening on port {PORT}...")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr}")
        handle_request(client_socket)

if __name__ == "__main__":
    start_server()
