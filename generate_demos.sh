#!/usr/bin/env bash

mkdir -p boards/

demos=(philosophers hello_world tensorflow_lite_micro shell_module micropython)
SCRIPT="cpu0 VectorTableOffset \`sysbus GetSymbolAddress \"_vector_table\"\`"

for i in "${!demos[@]}"
do
    # The JSON file created by Dashboard contains information on the board running the specified demo, test results, used serial port etc.
    wget -P /tmp https://zephyr-dashboard.renode.io/results-"${demos[i]}"_all.json
    board_names=( $(jq -r ' .[] | select(.status | contains("PASSED")) | .board_name' /tmp/results-"${demos[i]}"_all.json))
    board_path=( $(jq -r ' .[] | select(.status | contains("PASSED")) | .board_path' /tmp/results-"${demos[i]}"_all.json))
    uart_names=( $(jq -r ' .[] | select(.status | contains("PASSED")) | .uart_name' /tmp/results-"${demos[i]}"_all.json))
    readarray -t cpus < <(jq -r ' .[] | select(.status | contains("PASSED")) | .cpu' /tmp/results-"${demos[i]}"_all.json)
    for j in "${!board_path[@]}"
    do
        echo "${demos[i]} ${board_names[j]}"
        board_path="boards/${board_names[j]}"
        # First we replace Jinja templates in the demo-specific input. We'll use it later to fill out the Python template file
        jinja -D zephyr_platform ${board_names[j]} -D uart_name ${uart_names[j]} -o "/tmp/${board_names[j]}_${demos[i]}" ${demos[i]}
        sample=`cat /tmp/${board_names[j]}_${demos[i]}`
        if echo ${cpus[j]##*-> } | grep -q 'arm/armv.-m' ; then
            # For ARM Cortex-M platforms we explicitly initialize VTOR in the script, as the OS build system can place it in various parts of the binary.
            jinja -D sample_name ${demos[i]} -D sample "${sample}" -D zephyr_platform ${board_names[j]} -D board_path ${board_path} -D uart_name ${uart_names[j]} -D script "$SCRIPT" -o "${board_path}"_"${demos[i]}".py template.py
        else
            # For other platforms we simply replace template placeholders for basic demo data
            jinja -D sample_name ${demos[i]} -D sample "${sample}" -D zephyr_platform ${board_names[j]} -D board_path ${board_path} -D uart_name ${uart_names[j]} -o "${board_path}"_"${demos[i]}".py template.py
        fi
    done
done
