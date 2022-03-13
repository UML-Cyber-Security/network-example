openssl req -new -x509 -days 365 -nodes -out cert.pem -keyout cert.pem -subj "/CN=test.server/"
chmod 400 cert.pem
