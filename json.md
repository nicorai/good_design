{
  "name": "server01",
  "spec": {
    "cpu": 8,
    "memory": 32
  }
}

jq '.. | objects | keys[]' config.json | grep cpu

jq '.. | objects | keys[]' config.json

jq '.. | objects | select(has("port")) | .port' config.json


$ cat data.json | jq '.[] | select(.name == "John") | .age'