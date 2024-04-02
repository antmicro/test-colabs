#!/usr/bin/env bash
set -euo pipefail

mkdir -p boards/

zephyr_DEMOS=(philosophers hello_world tensorflow_lite_micro shell_module micropython blinky hello_world_user synchronization lz4 rust-app kenning-zephyr-runtime-microtvm kenning-zephyr-runtime-tflitemicro)
zephyr_dashboard_base=https://new-zephyr-dashboard.renode.io
zephyr_VERSION="$(curl -s $zephyr_dashboard_base/zephyr_sim/latest)"
zephyr_renode_version="$(curl -s $zephyr_dashboard_base/zephyr_sim/$zephyr_VERSION/latest)"
zephyr_DASHBOARD="$zephyr_dashboard_base/zephyr_sim/$zephyr_VERSION/$zephyr_renode_version"
uboot_DEMOS=(uboot)
uboot_DASHBOARD=https://u-boot-dashboard.renode.io
uboot_VERSION="$(curl -s $uboot_DASHBOARD/uboot.version)"

SET_VTOR="cpu0 VectorTableOffset \`sysbus GetSymbolAddress \"_vector_table\"\`"

tmp="$(mktemp --tmpdir -d renodepedia-colabs-XXXXXXXXXX)"
cleanup() {
    rm -rf "$tmp"
}
trap cleanup EXIT

wget() {
    command wget --retry-connrefused --waitretry=1 --read-timeout=10 --timeout=10 --tries 3 "$@"
}

generate_demos() {
    demos="${1}_DEMOS[@]"
    dashboard="${1}_DASHBOARD"
    version="${1}_VERSION"
    # Get Renode platform description files for all boards (and demos)
    mkdir "$tmp/$1"
    wget -P "$tmp" "${!dashboard}"/renodekit.tar.xz
    # Assumption: no two boards with different architectures will have the same name
    tar xf "$tmp/renodekit.tar.xz" -C "$tmp/$1" --wildcards '*.repl' --transform 's:.*/::g'
    rm "$tmp/renodekit.tar.xz"
    for demo in "${!demos}"
    do
        # The JSON file created by Dashboard contains information on the board running the specified demo, test results, used serial port etc.
        wget -P "$tmp" "${!dashboard}"/results-"${demo}"-all.json
        board_names=( $(jq -r ' .[] | select(.status | contains("PASSED")) | .platform' "$tmp"/results-"${demo}"-all.json))
        original_names=( $(jq -r ' .[] | select(.status | contains("PASSED")) | .platform_original' "$tmp"/results-"${demo}"-all.json))
        board_paths=( $(jq -r ' .[] | select(.status | contains("PASSED")) | .board_dir' "$tmp"/results-"${demo}"-all.json))
        uart_names=( $(jq -r ' .[] | select(.status | contains("PASSED")) | .uart_name' "$tmp"/results-"${demo}"-all.json))
        gpio_led_names=( $(jq -r ' .[] | select(.status | contains("PASSED")) | .peripherals["gpio-led"] | (.name + "." + .led_name)' "$tmp"/results-"${demo}"-all.json))
        readarray -t dts_chain < <(jq -r ' .[] | select(.status | contains("PASSED")) | .dts_include_chain | join(",")' "$tmp"/results-"${demo}"-all.json)
        for j in "${!board_paths[@]}"
        do
            platform="${board_names[j]}"
            platform_original="${original_names[j]}"
            echo "${demo} ${platform}"
            # Generate a script that halts every CPU except cpu0, if any are present
            repl_path="$tmp/${1}/$platform.repl"
            script="$(grep -Po '^.*(?=:\s+CPU\.)' "$repl_path" | { grep -Fxv cpu0 || :; } | while read -r c; do echo "$c IsHalted true"; done)"
            board_path="boards/${platform}"
            repl="${!dashboard}/${platform}-${demo}/${platform}-${demo}.repl"
            elf="${!dashboard}/${platform}-${demo}/${platform}-${demo}.elf"
            # On the Zephyr dashboard, the locations are different
            if [ "$1" = zephyr ]; then
                repl="${!dashboard}/${platform}/${demo}/${demo}.repl"
                # The binary is stored in a separate directory
                elf="$zephyr_dashboard_base/zephyr/${!version}/${platform}/${demo}/${demo}.elf"
            fi
            # First we replace Jinja templates in the demo-specific input. We'll use it later to fill out the Python template file
            jinja -D platform ${platform} -D platform_original ${platform_original} -D uart_name ${uart_names[j]} -D gpio_led_name ${gpio_led_names[j]} -D software_version "${!version}" -o "$tmp/${platform}_${demo}" ${demo}
            sample=`cat "${tmp}"/${platform}_${demo}`
            if [ "$1" = zephyr ] && echo ${dts_chain[j]##*-> } | grep -q 'arm/armv.-m' ; then
                # For ARM Cortex-M platforms we explicitly initialize VTOR in the script, as the OS build system can place it in various parts of the binary.
                script="$script${script:+$'\n'}$SET_VTOR"
            fi
            jinja -D sample_name ${demo} -D sample "${sample}" -D platform ${platform} -D platform_original ${platform_original} -D board_path ${board_path} -D uart_name ${uart_names[j]} -D script "$script" -D software_version "${!version}" -D repl "$repl" -D elf "$elf" -o "${board_path}"_"${demo}".py template.py
        done
    done
}

generate_demos zephyr
generate_demos uboot
