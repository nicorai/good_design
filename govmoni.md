## Go vmoni
- https://github.com/vmware/govmomi
- https://blogs.vmware.com/vmware-japan/2023/07/tam-blog-opearation_vsphere_with_govc.html


SET GOVC_URL=【vCenter Server の URL】
SET GOVC_USERNAME=【ユーザ名】
SET GOVC_PASSWORD=【パスワード】
SET GOVC_INSECURE=1 #自己証明書など、証明書の検証を行わない場合に指定する

govc の基本的な使い方は下記のようになっており、コマンドで行いたい操作を指定し実行します。
govc 【コマンド】 【オプション】(【対象インベントリオブジェクト】)

例えば仮想マシンの一覧は以下で取得できます。

govc ls -t VirtualMachine */*

for vm in $(govc ls /DC1/vm); do
    govc vm.info "$vm" | \
    grep -E '^(Name:|  Host:|  Path:|  Power state:)'
done

printf "VM名\tホスト名\tデータストア名\tPower\n"

govc find / -type m | while read vm; do
    govc vm.info "$vm" | awk '
        /^Name:/        { name=$2 }
        /^  Host:/      { host=$2 }
        /^  Path:/      {
            match($0, /\[([^]]+)\]/, a)
            ds=a[1]
        }
        /^  Power state:/ {
            print name "\t" host "\t" ds "\t" $3
        }
    '
done

govc find / -type m | while read vm; do
  govc vm.info -json "$vm"
done | jq -r '
  .VirtualMachines[] |
  [
    .Name,
    .Runtime.Host.Value,
    (.Datastore[0].Value // ""),
    .Runtime.PowerState
  ] | @tsv
'





#!/bin/bash

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

# VM
govc object.collect -json -type m / \
    name summary.runtime.host datastore runtime.powerState \
    > "$tmp/vm.json"

# ESXi
govc object.collect -json -type h / \
    name parent \
    > "$tmp/host.json"

# Cluster
govc object.collect -json -type c / \
    name \
    > "$tmp/cluster.json"

jq -rn \
  --slurpfile vm "$tmp/vm.json" \
  --slurpfile host "$tmp/host.json" \
  --slurpfile cluster "$tmp/cluster.json" '

  # ここでVM/Host/ClusterをIDで関連付け
  # VM -> Host -> Cluster

  $vm[0][]
'