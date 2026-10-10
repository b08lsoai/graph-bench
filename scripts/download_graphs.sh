#!/bin/bash
#
# Download all SuiteSparse matrix-market graphs used by the MST (Boruvka)
# benchmark. Matrices are not stored in the repo; run this script once after
# cloning to fetch every .mtx file into the dataset directory.
#
# The list mirrors the `GRAPHS_MST` set in scripts/dataset.py:
#   nemeth15 1138_bus G10 c-73 il2010 GaAsH6 ky2010
#   CurlCurl_3 kron_g500-logn21 Spielman_k200 Spielman_k300 Spielman_k600
#   Queen_4147 nlpkkt160 nlpkkt240 GAP-road
#
# Each graph is defined as "PART/GROUP/NAME.tar.gz" (e.g. "MM/DIMACS10/ky2010").
# The full URL is https://sparse.tamu.edu/<PART/GROUP/NAME>.tar.gz
#
# All graphs must be CONNECTED and WEIGHTED: the MST benchmark compares
# tools that require connectivity (gunrock's Boruvka throws on
# disconnected graphs), so disconnected graphs (e.g. human_gene2,
# mawi_201512012345) are intentionally excluded.
#
# Usage:
#   ./download_graphs.sh                    download all graphs
#   ./download_graphs.sh ky2010 GAP-road    download only the listed graphs
#
# Options:
#   TARGET_DIR=<path> ./download_graphs.sh  extract into <path> (default: dataset/)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${TARGET_DIR:-$(dirname "$SCRIPT_DIR")/dataset}"

BASE_URL="https://sparse.tamu.edu"

# PART/GROUP/NAME of each graph to download.
# Weighted, undirected, connected graphs suitable for the MST (Boruvka)
# benchmark.
GRAPHS=(
    "MM/Nemeth/nemeth15"
    "MM/HB/1138_bus"
    "MM/Gset/G10"
    "MM/Schenk_IBMNA/c-73"
    "MM/DIMACS10/il2010"
    "MM/PARSEC/GaAsH6"
    "MM/DIMACS10/ky2010" # 2 компоненты
    "MM/Bodendiek/CurlCurl_3"
    "MM/DIMACS10/kron_g500-logn21" # не связный
    "MM/FlowIPM22/Spielman_k200"
    "MM/FlowIPM22/Spielman_k300"
    "MM/FlowIPM22/Spielman_k600"
    "MM/Janna/Queen_4147" # не связный
    "MM/Schenk/nlpkkt160"
    "MM/Schenk/nlpkkt240"
    "MM/GAP/GAP-road"
)

download_graph() {
    local graph="$1"
    local url="$BASE_URL/$graph.tar.gz"
    local archive
    archive="$(basename "$graph").tar.gz"
    local name
    name="$(basename "$graph").mtx"

    if [[ -f "$TARGET_DIR/$name" ]]; then
        echo "[skip] $name already exists in $TARGET_DIR"
        return 0
    fi

    echo "[download] $url"
    wget -q --show-progress "$url"

    echo "[extract] $archive -> $TARGET_DIR"
    tar -xzf "$archive" -C "$TARGET_DIR"

    echo "[cleanup] remove $archive"
    rm "$archive"

    ls -l "$TARGET_DIR/$name"
}

if [[ $# -gt 0 ]]; then
    selected=("$@")
else
    selected=("${GRAPHS[@]}")
fi

mkdir -p "$TARGET_DIR"

for graph in "${selected[@]}"; do
    download_graph "$graph"
done

echo "Done. Extracted to $TARGET_DIR"