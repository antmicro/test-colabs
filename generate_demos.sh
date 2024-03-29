#!/usr/bin/env bash

mkdir -p boards/

zephyr_DEMOS=(philosophers hello_world tensorflow_lite_micro shell_module micropython blinky hello_world_user synchronization lz4 rust-app kenning-zephyr-runtime-microtvm kenning-zephyr-runtime-tflitemicro)
zephyr_DASHBOARD=https://zephyr-dashboard.renode.io
zephyr_VERSION="$(curl -s $zephyr_DASHBOARD/zephyr.version)"
uboot_DEMOS=(uboot)
uboot_DASHBOARD=https://u-boot-dashboard.renode.io
uboot_VERSION="$(curl -s $uboot_DASHBOARD/uboot.version)"

SCRIPT="cpu0 VectorTableOffset \`sysbus GetSymbolAddress \"_vector_table\"\`"

tmp="$(mktemp --tmpdir -d renodepedia-colabs-XXXXXXXXXX)"
cleanup() {
    rm -rf "$tmp"
}
trap cleanup EXIT

generate_demos() {
    demos="${1}_DEMOS[@]"
    dashboard="${1}_DASHBOARD"
    version="${1}_VERSION"
    for demo in "${!demos}"
    do
        # The JSON file created by Dashboard contains information on the board running the specified demo, test results, used serial port etc.
        wget -P "$tmp" "${!dashboard}"/results-"${demo}"-all.json
        board_names=( $(jq -r ' .[] | select(.status | contains("PASSED")) | .platform' "$tmp"/results-"${demo}"-all.json))
        board_path=( $(jq -r ' .[] | select(.status | contains("PASSED")) | .board_dir' "$tmp"/results-"${demo}"-all.json))
        uart_names=( $(jq -r ' .[] | select(.status | contains("PASSED")) | .uart_name' "$tmp"/results-"${demo}"-all.json))
        gpio_led_names=( $(jq -r ' .[] | select(.status | contains("PASSED")) | .peripherals["gpio-led"] | (.name + "." + .led_name)' "$tmp"/results-"${demo}"-all.json))
        readarray -t dts_chain < <(jq -r ' .[] | select(.status | contains("PASSED")) | .dts_include_chain | join(",")' "$tmp"/results-"${demo}"-all.json)
        for j in "${!board_path[@]}"
        do
            platform="${board_names[j]}"
            echo "${demo} ${platform}"
            board_path="boards/${platform}"
            repl="${!dashboard}/${platform}-${demo}/${platform}-${demo}.repl"
            elf="${!dashboard}/${platform}-${demo}/${platform}-${demo}.elf"
            # On the Zephyr dashboard, binaries are stored separately
            if [ "$1" = zephyr ]; then
                elf="https://new-zephyr-dashboard.renode.io/zephyr/${!version}/${platform}/${demo}/${demo}.elf"
            fi
            # First we replace Jinja templates in the demo-specific input. We'll use it later to fill out the Python template file
            jinja -D platform ${platform} -D uart_name ${uart_names[j]} -D gpio_led_name ${gpio_led_names[j]} -D software_version "${!version}" -o "$tmp/${platform}_${demo}" ${demo}
            sample=`cat "${tmp}"/${platform}_${demo}`
            if [ "$1" = zephyr ] && echo ${dts_chain[j]##*-> } | grep -q 'arm/armv.-m' ; then
                # For ARM Cortex-M platforms we explicitly initialize VTOR in the script, as the OS build system can place it in various parts of the binary.
                jinja -D sample_name ${demo} -D sample "${sample}" -D platform ${platform} -D board_path ${board_path} -D uart_name ${uart_names[j]} -D script "$SCRIPT" -D software_version "${!version}" -D repl "$repl" -D elf "$elf" -o "${board_path}"_"${demo}".py template.py
            else
                # For other platforms we simply replace template placeholders for basic demo data
                jinja -D sample_name ${demo} -D sample "${sample}" -D platform ${platform} -D board_path ${board_path} -D uart_name ${uart_names[j]} -D software_version "${!version}" -D repl "$repl" -D elf "$elf" -o "${board_path}"_"${demo}".py template.py
            fi
        done
    done
}

generate_demos zephyr
generate_demos uboot
