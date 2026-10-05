#!/usr/bin/env bash
set -eu

if [ "$(id -u)" -ne 0 ]; then
  echo "Run with sudo: sudo bash ./generate-certs.sh" >&2
  exit 1
fi

cd "$(dirname "$0")"
for file in \
  certs/authority/ca.key \
  certs/authority/ca.crt \
  certs/elasticsearch/elasticsearch.key \
  certs/elasticsearch/elasticsearch.crt \
  certs/opencti/ca.crt; do
  if [ -e "$file" ]; then
    echo "Refusing to overwrite existing certificate material: $file" >&2
    exit 1
  fi
done

umask 077
mkdir -p certs/authority certs/elasticsearch certs/opencti
chmod 700 certs/authority
chmod 755 certs certs/elasticsearch certs/opencti

openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:4096 -out certs/authority/ca.key
openssl req -x509 -new -key certs/authority/ca.key -sha256 -days 3650 \
  -out certs/authority/ca.crt \
  -subj "/CN=OpenCTI Elasticsearch local CA"

openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 \
  -out certs/elasticsearch/elasticsearch.key
openssl req -new -key certs/elasticsearch/elasticsearch.key \
  -out certs/elasticsearch/elasticsearch.csr \
  -subj "/CN=elasticsearch" \
  -addext "subjectAltName=DNS:elasticsearch,DNS:localhost,IP:127.0.0.1" \
  -addext "keyUsage=digitalSignature,keyEncipherment" \
  -addext "extendedKeyUsage=serverAuth,clientAuth"
openssl x509 -req -in certs/elasticsearch/elasticsearch.csr \
  -CA certs/authority/ca.crt -CAkey certs/authority/ca.key -CAcreateserial \
  -out certs/elasticsearch/elasticsearch.crt -days 825 -sha256 \
  -copy_extensions copy

cp certs/authority/ca.crt certs/elasticsearch/ca.crt
cp certs/authority/ca.crt certs/opencti/ca.crt
chown 1000:0 certs/elasticsearch/elasticsearch.key
chmod 640 certs/elasticsearch/elasticsearch.key
chmod 644 certs/authority/ca.crt certs/elasticsearch/elasticsearch.crt \
  certs/elasticsearch/ca.crt certs/opencti/ca.crt

openssl verify -CAfile certs/authority/ca.crt certs/elasticsearch/elasticsearch.crt
