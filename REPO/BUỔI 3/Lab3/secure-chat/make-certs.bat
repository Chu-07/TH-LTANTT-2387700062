@echo off
setlocal

set "OPENSSL=C:\Program Files\OpenSSL-Win64\bin\openssl.exe"

cd /d "%~dp0"

echo ===============================
echo Tao thu muc chung chi...
echo ===============================

if not exist certs mkdir certs
if not exist certs\ca mkdir certs\ca
if not exist certs\server mkdir certs\server
if not exist certs\client mkdir certs\client

echo.
echo [1] Tao CA private key...
"%OPENSSL%" genrsa -out certs\ca\ca.key 2048

echo.
echo [2] Tao CA certificate...
"%OPENSSL%" req -x509 -new -nodes ^
-key certs\ca\ca.key ^
-sha256 ^
-days 3650 ^
-out certs\ca\ca.crt ^
-config openssl.cnf ^
-extensions v3_ca

echo.
echo [3] Tao Server private key...
"%OPENSSL%" genrsa -out certs\server\server.key 2048

echo.
echo [4] Tao Server CSR...
"%OPENSSL%" req -new ^
-key certs\server\server.key ^
-out certs\server\server.csr ^
-subj "/C=VN/ST=HN/L=HN/O=MyOrg/OU=IT Dept/CN=localhost"

echo.
echo [5] Ky Server certificate...
"%OPENSSL%" x509 -req ^
-in certs\server\server.csr ^
-CA certs\ca\ca.crt ^
-CAkey certs\ca\ca.key ^
-CAcreateserial ^
-out certs\server\server.crt ^
-days 365 ^
-sha256

echo.
echo [6] Tao Client private key...
"%OPENSSL%" genrsa -out certs\client\client.key 2048

echo.
echo [7] Tao Client CSR...
"%OPENSSL%" req -new ^
-key certs\client\client.key ^
-out certs\client\client.csr ^
-subj "/C=VN/ST=HN/L=HN/O=MyOrg/OU=IT Dept/CN=client"

echo.
echo [8] Ky Client certificate...
"%OPENSSL%" x509 -req ^
-in certs\client\client.csr ^
-CA certs\ca\ca.crt ^
-CAkey certs\ca\ca.key ^
-CAcreateserial ^
-out certs\client\client.crt ^
-days 365 ^
-sha256

echo.
echo ===============================
echo CAC CHUNG CHI DA TAO XONG
echo ===============================

echo CA:
echo certs\ca\ca.crt

echo Server:
echo certs\server\server.crt

echo Client:
echo certs\client\client.crt

echo ===============================

pause