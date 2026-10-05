# OpenCTI Docker Compose

OpenCTI 6.9.29 の小規模構成です。OpenCTI、Elasticsearch、Redis、MinIO、RabbitMQ、worker 1 台を起動します。connector は含めていません。

Elasticsearch と OpenCTI の通信は自己署名 CA による HTTPS です。証明書と認証情報は環境ごとに新しく生成してください。このフォルダーを複数環境で使い回す場合も、`.env` と `certs/` は環境間でコピーしないでください。

## 前提

- Linux ホスト、Docker Engine と Docker Compose v2
- OpenSSL 3 以上
- 目安として RAM 16 GB 以上、ディスク空き 30 GB 以上
- Elasticsearch の `vm.max_map_count` が 262144 以上

Ubuntu/Debian では、必要なら次を実行します。

```sh
sudo sysctl -w vm.max_map_count=262144
```

再起動後も維持する場合は `/etc/sysctl.d/99-opencti.conf` に `vm.max_map_count=262144` を設定します。

## 初回セットアップ

1. この `opencti` フォルダーを Docker ホストへコピーして移動します。
1. 環境変数ファイルを作成します。

```sh
cp .env.example .env
chmod 600 .env
```

1. `.env` を編集します。`OPENCTI_HOST` にはアクセスに使う DNS 名または IP アドレスを設定します。`OPENCTI_ADMIN_EMAIL` と `OPENCTI_ADMIN_PASSWORD` も必ず変更してください。`ELASTIC_PASSWORD`、`MINIO_ROOT_PASSWORD`、`RABBITMQ_DEFAULT_PASS`、`OPENCTI_ADMIN_TOKEN`、`OPENCTI_HEALTHCHECK_ACCESS_KEY` はそれぞれ別々の値にします。例:

```sh
openssl rand -hex 32
```

`OPENCTI_ENCRYPTION_KEY` は 32 文字の hex 値にします。

```sh
openssl rand -hex 16
```

1. この環境専用の自己署名 CA と Elasticsearch 証明書を生成します。

```sh
sudo bash ./generate-certs.sh
```

生成スクリプトは SAN に `DNS:elasticsearch`、`DNS:localhost`、`IP:127.0.0.1` を含む証明書を作り、署名検証します。`certs/authority/ca.key` は CA の秘密鍵なので安全に保管し、他の環境へ共有しないでください。`certs/` と `.env` は Git に登録しない設定です。

1. 起動します。

```sh
docker compose config --quiet
docker compose up -d
docker compose ps
```

Elasticsearch と OpenCTI が `healthy` になるまで数分かかることがあります。ブラウザーから `http://<OPENCTI_HOST>:<OPENCTI_PORT>` を開きます。

ホスト自身から Elasticsearch を確認する場合は、`.env` の `ELASTICSEARCH_HOST_PORT`（既定値 `9200`）で `127.0.0.1` にのみ公開されます。CA を指定し、curl のパスワードプロンプトで `ELASTIC_PASSWORD` を入力します。

```sh
curl --cacert certs/authority/ca.crt --user elastic https://localhost:9200/
```

このポートは loopback 限定なので、他のマシンからは接続できません。OpenCTI から Elasticsearch への内部通信は引き続き `https://elasticsearch:9200` を使用します。

## 運用

ログ確認:

```sh
docker compose logs -f elasticsearch opencti
```

停止:

```sh
docker compose down
```

`docker compose down -v` は Elasticsearch を含む保存データを削除するため、通常の停止には使わないでください。

この構成で TLS を有効にするのは Elasticsearch と OpenCTI の間です。ブラウザーから OpenCTI まで HTTPS にする場合は、別途リバースプロキシと公開用証明書を設定してください。
