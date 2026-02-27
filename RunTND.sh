#!/bin/bash

ModifyFile="ModifySourceCode.py"
RunFile="RunAlgo.py"

if [ -z "$1" ]; then
    echo "Usage: $0 <argument>"
    exit 1
fi

input_arg="$1"


python3 "$ModifyFile" $input_arg

