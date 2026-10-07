import socket
import ssl
import threading
import os
import binascii

from message_encryption import MessageEncryption


SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8443

CA_CERT = "certs/ca/ca.crt"
CLIENT_CERT = "certs/client/client.crt"
CLIENT_KEY = "certs/client/client.key"


def receive_messages(ssl_sock, encryption):
    try:
        while True:
            encrypted_data = ssl_sock.recv(4096)

            if not encrypted_data:
                break

            try:
                message = encryption.decrypt(encrypted_data)

                print(f"\n{message}")
                print("> ", end="", flush=True)

            except Exception as e:
                print(f"\n[-] Failed to decrypt message: {e}")

    except Exception as e:
        print(f"\n[-] Connection closed: {e}")


def main():
    username = input("Username: ").strip()

    if not username:
        print("Username cannot be empty.")
        return

    aes_key = os.urandom(32)

    encryption = MessageEncryption(aes_key)

    context = ssl.create_default_context(
        ssl.Purpose.SERVER_AUTH,
        cafile=CA_CERT
    )

    context.minimum_version = ssl.TLSVersion.TLSv1_2

    context.load_cert_chain(
        certfile=CLIENT_CERT,
        keyfile=CLIENT_KEY
    )

    context.check_hostname = False

    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    ssl_sock = context.wrap_socket(
        sock,
        server_hostname="localhost"
    )

    print(
        f"[+] Connecting to "
        f"{SERVER_HOST}:{SERVER_PORT}..."
    )

    ssl_sock.connect(
        (SERVER_HOST, SERVER_PORT)
    )

    print(
        "[+] TLS connection established:",
        ssl_sock.version()
    )

    print(
        "[+] Server certificate:",
        ssl_sock.getpeercert()
    )

    key_hex = binascii.hexlify(
        aes_key
    ).decode()

    init_message = (
        f"{username}:{key_hex}"
    ).encode()

    ssl_sock.sendall(
        init_message
    )

    thread = threading.Thread(
        target=receive_messages,
        args=(ssl_sock, encryption),
        daemon=True
    )

    thread.start()

    print()
    print("Type messages.")
    print("Type 'exit' to quit.")

    try:
        while True:
            message = input("> ")

            if message.lower() == "exit":
                break

            if not message:
                continue

            encrypted_message = encryption.encrypt(
                message
            )

            ssl_sock.sendall(
                encrypted_message
            )

    except KeyboardInterrupt:
        pass

    finally:
        ssl_sock.close()

        print(
            "[-] Disconnected."
        )


if __name__ == "__main__":
    main()