#!/bin/bash

ES="http://localhost:9200"

echo "INDEX SHARD PRIREP ES_NODE K8S_NODE VM ESXI DATASTORE"

curl -s "$ES/_cat/shards?h=index,shard,prirep,node" |
while read index shard prirep esnode
do
    # ES Node名 → Pod
    pod=$(kubectl get pods -A -o json |
        jq -r --arg n "$esnode" '
          .items[]
          | select(.metadata.name == $n)
          | .metadata.name
        ' | head -1)

    # Pod → Kubernetes Node
    k8snode=$(kubectl get pod "$pod" -A \
        -o jsonpath='{.spec.nodeName}' 2>/dev/null)

    # Kubernetes Node → VCSA VM
    vm=$(govc find / -type m -name "$k8snode" 2>/dev/null | head -1)

    # VM → ESXi
    esxi=$(govc vm.info "$vm" 2>/dev/null |
        awk -F': ' '/Host:/ {print $2}')

    # VM → Datastore
    datastore=$(govc vm.info -json "$vm" 2>/dev/null |
        jq -r '.VirtualMachines[0].Datastore[]?.Name' |
        paste -sd ',' -)

    printf "%s %s %s %s %s %s %s %s\n" \
        "$index" "$shard" "$prirep" "$esnode" \
        "$k8snode" "$k8snode" "$esxi" "$datastore"
done