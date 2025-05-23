#!/usr/bin/env bash
set -euo pipefail

mkdir -p boards/

zephyr_DEMOS=(philosophers hello_world tensorflow_lite_micro shell_module micropython blinky hello_world_user synchronization lz4 rust-app kenning-zephyr-runtime-microtvm kenning-zephyr-runtime-tflitemicro kenning-zephyr-runtime-iree)
zephyr_dashboard_base=https://zephyr-dashboard.renode.io
zephyr_VERSION="$(curl -s $zephyr_dashboard_base/zephyr_sim/latest)"
zephyr_renode_version="$(curl -s $zephyr_dashboard_base/zephyr_sim/$zephyr_VERSION/latest)"
zephyr_DASHBOARD="$zephyr_dashboard_base/zephyr_sim/$zephyr_VERSION/$zephyr_renode_version"
zephyr_DASHBOARD_BUILD="$zephyr_dashboard_base/zephyr/$zephyr_VERSION"

uboot_DEMOS=(uboot)
uboot_dashboard_base=https://u-boot-dashboard.renode.io
uboot_VERSION="$(curl -s $uboot_dashboard_base/uboot_sim/latest)"
uboot_renode_version="$(curl -s $uboot_dashboard_base/uboot_sim/$uboot_VERSION/latest)"
uboot_DASHBOARD="$uboot_dashboard_base/uboot_sim/$uboot_VERSION/$uboot_renode_version"
uboot_DASHBOARD_BUILD="$uboot_dashboard_base/uboot/$uboot_VERSION"

tmp="$(mktemp --tmpdir -d renodepedia-colabs-XXXXXXXXXX)"
cleanup() {
    rm -rf "$tmp"
}
trap cleanup EXIT

wget() {
    command wget -nv --retry-connrefused --waitretry=1 --read-timeout=10 --timeout=10 --tries 3 "$@"
}

generate_demos() {
    demos="${1}_DEMOS[@]"
    dashboard="${1}_DASHBOARD"
    build_dashboard="${1}_DASHBOARD_BUILD"
    version="${1}_VERSION"
    # Get Renode platform description files for all boards (and demos)
    mkdir "$tmp/$1"
    wget -P "$tmp" "${!dashboard}"/replkit.tar.xz
    # Assumption: no two boards with different architectures will have the same name
    tar xf "$tmp/replkit.tar.xz" -C "$tmp/$1" --wildcards '*.resc' --transform 's:.*/::g'
    rm "$tmp/replkit.tar.xz"
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

            board_path="boards/${platform}"
            repl="${!dashboard}/${platform}/${demo}/${demo}.repl"
            elf="${!build_dashboard}/${platform}/${demo}/${demo}.elf"
            
            resc_path="$tmp/${1}/$platform-$demo.resc"
            script=$(cat $resc_path | sed -e "/machine LoadPlatformDescription/c\machine LoadPlatformDescription @${repl}\nmachine EnableProfiler \$ORIGIN/metrics.dump")

            # First we replace Jinja templates in the demo-specific input. We'll use it later to fill out the Python template file
            jinja -D platform ${platform} -D platform_original ${platform_original} -D uart_name ${uart_names[j]} -D gpio_led_name ${gpio_led_names[j]} -D software_version "${!version}" -o "$tmp/${platform}_${demo}" ${demo}
            sample=`cat "${tmp}"/${platform}_${demo}`
            jinja -D sample_name ${demo} -D sample "${sample}" -D platform ${platform} -D platform_original ${platform_original} -D board_path ${board_path} -D uart_name ${uart_names[j]} -D script "$script" -D software_version "${!version}" -D repl "$repl" -D elf "$elf" -o "${board_path}"_"${demo}".py template.py
        done
    done
}

generate_demos zephyr
generate_demos uboot
