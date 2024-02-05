#!/usr/bin/env bash

mkdir -p boards/

demos=(philosophers hello_world tensorflow_lite_micro shell_module micropython blinky hello_world_user synchronization lz4 rust-app)
SCRIPT="cpu0 VectorTableOffset \`sysbus GetSymbolAddress \"_vector_table\"\`"
ZEPHYR_VERSION="$(curl -s https://zephyr-dashboard.renode.io/zephyr.version)"

for i in "${!demos[@]}"
do
    # The JSON file created by Dashboard contains information on the board running the specified demo, test results, used serial port etc.
    wget -P /tmp https://zephyr-dashboard.renode.io/results-"${demos[i]}"-all.json
    board_names=( $(jq -r ' .[] | select(.status | contains("PASSED")) | .platform' /tmp/results-"${demos[i]}"-all.json))
    board_path=( $(jq -r ' .[] | select(.status | contains("PASSED")) | .board_dir' /tmp/results-"${demos[i]}"-all.json))
    uart_names=( $(jq -r ' .[] | select(.status | contains("PASSED")) | .uart_name' /tmp/results-"${demos[i]}"-all.json))
    gpio_led_names=( $(jq -r ' .[] | select(.status | contains("PASSED")) | .peripherals["gpio-led"] | (.name + "." + .led_name)' /tmp/results-"${demos[i]}"-all.json))
    readarray -t cpus < <(jq -r ' .[] | select(.status | contains("PASSED")) | .dts_include_chain | join(",")' /tmp/results-"${demos[i]}"-all.json)
    for j in "${!board_path[@]}"
    do
        echo "${demos[i]} ${board_names[j]}"
        board_path="boards/${board_names[j]}"
        # First we replace Jinja templates in the demo-specific input. We'll use it later to fill out the Python template file
        jinja -D zephyr_platform ${board_names[j]} -D uart_name ${uart_names[j]} -D gpio_led_name ${gpio_led_names[j]} -D zephyr_version "$ZEPHYR_VERSION" -o "/tmp/${board_names[j]}_${demos[i]}" ${demos[i]}
        sample=`cat /tmp/${board_names[j]}_${demos[i]}`
        if echo ${cpus[j]##*-> } | grep -q 'arm/armv.-m' ; then
            # For ARM Cortex-M platforms we explicitly initialize VTOR in the script, as the OS build system can place it in various parts of the binary.
            jinja -D sample_name ${demos[i]} -D sample "${sample}" -D zephyr_platform ${board_names[j]} -D board_path ${board_path} -D uart_name ${uart_names[j]} -D script "$SCRIPT" -D zephyr_version "$ZEPHYR_VERSION" -o "${board_path}"_"${demos[i]}".py template.py
        else
            # For other platforms we simply replace template placeholders for basic demo data
            jinja -D sample_name ${demos[i]} -D sample "${sample}" -D zephyr_platform ${board_names[j]} -D board_path ${board_path} -D uart_name ${uart_names[j]} -D zephyr_version "$ZEPHYR_VERSION" -o "${board_path}"_"${demos[i]}".py template.py
        fi
    done
done
