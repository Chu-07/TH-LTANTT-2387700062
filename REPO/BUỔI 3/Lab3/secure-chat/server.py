import socket
import ssl
import threading

from connection_manager import ConnectionManager
from room_manager import RoomManager
from message_encryption import MessageEncryption


HOST = "127.0.0.1"
PORT = 8443

SERVER_CERT = "certs/server/server.crt"
SERVER_KEY = "certs/server/server.key"
CA_CERT = "certs/ca/ca.crt"


connection_manager = ConnectionManager()
room_manager = RoomManager()


def handle_client(connstream, addr):
    print(f"[+] Client connected: {addr}")

    try:
        # Client gửi thông tin theo dạng:
        # username:key_hex
        data = connstream.recv(1024).decode("utf-8")

        if ":" not in data:
            print("[-] Invalid client initialization")
            return

        username, key_hex = data.split(":", 1)

        encryption_key = bytes.fromhex(key_hex)

        connection_manager.add_client(
            connstream,
            username,
            encryption_key
        )

        room_manager.create_room("general")
        room_manager.join_room("general", connstream)

        encryption = MessageEncryption(encryption_key)

        print(f"[+] User joined: {username}")

        while True:
            encrypted_message = connstream.recv(4096)

            if not encrypted_message:
                break

            try:
                message = encryption.decrypt(encrypted_message)

            except Exception as e:
                print(f"[-] Decryption failed: {e}")
                continue

            print(f"[{username}]: {message}")

            output_message = f"[{username}]: {message}"

            # Gửi tin nhắn cho các client khác
            with connection_manager.lock:

                for client_sock, info in list(
                    connection_manager.clients.items()
                ):

                    if client_sock != connstream:

                        try:
                            client_encryption = MessageEncryption(
                                info["encryption_key"]
                            )

                            encrypted_output = client_encryption.encrypt(
                                output_message
                            )

                            client_sock.sendall(
                                encrypted_output
                            )

                        except Exception as e:
                            print(
                                f"[-] Send error to "
                                f"{info['username']}: {e}"
                            )

    except Exception as e:
        print(f"[-] Exception: {e}")

    finally:
        print(f"[-] Client disconnected: {addr}")

        connection_manager.remove_client(connstream)

        room_manager.leave_room(
            "general",
            connstream
        )

        try:
            connstream.shutdown(
                socket.SHUT_RDWR
            )
        except Exception:
            pass

        connstream.close()


def main():

    context = ssl.SSLContext(
        ssl.PROTOCOL_TLS_SERVER
    )

    # Dùng TLS 1.2 trở lên
    context.minimum_version = ssl.TLSVersion.TLSv1_2

    context.load_cert_chain(
        certfile=SERVER_CERT,
        keyfile=SERVER_KEY
    )

    context.load_verify_locations(
        cafile=CA_CERT
    )

    # Bắt buộc client phải có certificate hợp lệ
    context.verify_mode = ssl.CERT_REQUIRED

    server_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server_socket.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    server_socket.bind(
        (HOST, PORT)
    )

    server_socket.listen(5)

    print(
        f"[+] SecureChat Server listening "
        f"on {HOST}:{PORT}"
    )

    print("[+] TLS minimum version: TLS 1.2")
    print("[+] Client certificate required")

    while True:

        client_socket, addr = server_socket.accept()

        try:
            connstream = context.wrap_socket(
                client_socket,
                server_side=True
            )

            print(
                "[+] TLS connection established:",
                connstream.version()
            )

            print(
                "[+] Client certificate:",
                connstream.getpeercert()
            )

            thread = threading.Thread(
                target=handle_client,
                args=(connstream, addr),
                daemon=True
            )

            thread.start()

        except ssl.SSLError as e:
            print(f"[-] SSL Error: {e}")
            client_socket.close()


if __name__ == "__main__":
    main()