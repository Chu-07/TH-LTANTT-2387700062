import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend


class MessageEncryption:
    def __init__(self, key=None):
        self.key = key if key is not None else os.urandom(32)
        self.backend = default_backend()

    def encrypt(self, plaintext):
        iv = os.urandom(16)

        cipher = Cipher(
            algorithms.AES(self.key),
            modes.CBC(iv),
            backend=self.backend
        )

        encryptor = cipher.encryptor()

        padder = padding.PKCS7(128).padder()

        padded_data = (
            padder.update(plaintext.encode("utf-8"))
            + padder.finalize()
        )

        ciphertext = (
            encryptor.update(padded_data)
            + encryptor.finalize()
        )

        return iv + ciphertext

    def decrypt(self, ciphertext):
        iv = ciphertext[:16]
        ct = ciphertext[16:]

        cipher = Cipher(
            algorithms.AES(self.key),
            modes.CBC(iv),
            backend=self.backend
        )

        decryptor = cipher.decryptor()

        padded_data = (
            decryptor.update(ct)
            + decryptor.finalize()
        )

        unpadder = padding.PKCS7(128).unpadder()

        data = (
            unpadder.update(padded_data)
            + unpadder.finalize()
        )

        return data.decode("utf-8")