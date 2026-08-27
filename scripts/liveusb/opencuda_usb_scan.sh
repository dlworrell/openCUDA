#!/usr/bin/env bash
set -uo pipefail

readonly SCAN_VERSION="0.1.0"
readonly DEFAULT_ABORT_TEMP_C=80
readonly DEFAULT_IDLE_SECONDS=600
readonly DEFAULT_PARTIAL_SECONDS=900
readonly DEFAULT_FULL_SECONDS=1800
readonly DEFAULT_MEMORY_MIB=512
readonly DEFAULT_EXPECTED_K80_DEVICES=2

ABORT_TEMP_C="${OPENCUDA_ABORT_TEMP_C:-$DEFAULT_ABORT_TEMP_C}"
IDLE_SECONDS="${OPENCUDA_IDLE_SECONDS:-$DEFAULT_IDLE_SECONDS}"
PARTIAL_SECONDS="${OPENCUDA_PARTIAL_SECONDS:-$DEFAULT_PARTIAL_SECONDS}"
FULL_SECONDS="${OPENCUDA_FULL_SECONDS:-$DEFAULT_FULL_SECONDS}"
MEMORY_MIB="${OPENCUDA_MEMORY_MIB:-$DEFAULT_MEMORY_MIB}"
EXPECTED_K80_DEVICES="${OPENCUDA_EXPECTED_K80_DEVICES:-$DEFAULT_EXPECTED_K80_DEVICES}"
RESULT_ROOT=""
RUN_DIR=""
REPORT=""
EVENT_LOG=""
TELEMETRY=""
LOAD_PID=""
MONITOR_PID=""
ABORT_FILE=""
WIFI_CONNECTION=""
FINAL_STATUS="INCOMPLETE"
K80_DEVICE_LIST=""
CURRENT_STAGE="inventory"

cleanup() {
    if [[ -n "$LOAD_PID" ]]; then
        kill "$LOAD_PID" 2>/dev/null || true
    fi
    if [[ -n "$MONITOR_PID" ]]; then
        kill "$MONITOR_PID" 2>/dev/null || true
    fi
    if [[ -n "$WIFI_CONNECTION" ]] && command -v nmcli >/dev/null 2>&1; then
        nmcli connection delete id "$WIFI_CONNECTION" >/dev/null 2>&1 || true
    fi
}
trap cleanup EXIT INT TERM

log() {
    local message="$*"
    printf '[%s] %s\n' "$(date -u +'%Y-%m-%dT%H:%M:%SZ')" "$message" | tee -a "$EVENT_LOG"
}

section() {
    printf '\n## %s\n\n' "$1" >>"$REPORT"
}

sanitize_stream() {
    sed -E \
        -e 's/^([[:space:]]*(Serial Number|UUID|Asset Tag|Service Tag|Chassis Serial|Board Serial)[[:space:]]*:[[:space:]]*).*/\1[REDACTED]/I' \
        -e 's/^([[:space:]]*iSerial[[:space:]]+[0-9]+[[:space:]]+).*/\1[REDACTED]/I' \
        -e 's/(GPU UUID[[:space:]]*:[[:space:]]*).*/\1[REDACTED]/I' \
        -e 's/([[:xdigit:]]{2}:){5}[[:xdigit:]]{2}/[REDACTED-MAC]/g' \
        -e 's/([[:space:]]serial=)[^[:space:]]+/\1[REDACTED]/Ig'
}

capture() {
    local title="$1"
    shift
    section "$title"
    printf '```text\n' >>"$REPORT"
    if command -v "$1" >/dev/null 2>&1; then
        "$@" 2>&1 | sanitize_stream >>"$REPORT" || printf '[command exited non-zero]\n' >>"$REPORT"
    else
        printf '[command unavailable: %s]\n' "$1" >>"$REPORT"
    fi
    printf '```\n' >>"$REPORT"
}

find_result_root() {
    local target=""
    if [[ -n "${OPENCUDA_RESULT_ROOT:-}" ]]; then
        RESULT_ROOT="$OPENCUDA_RESULT_ROOT"
        mkdir -p "$RESULT_ROOT"
        return
    fi
    if command -v findmnt >/dev/null 2>&1; then
        target="$(findmnt -rn -S LABEL=OPENCUDA_DATA -o TARGET 2>/dev/null | head -n1)"
    fi
    if [[ -n "$target" && -w "$target" ]]; then
        RESULT_ROOT="$target/opencuda-results"
    elif [[ -d /var/lib/opencuda && -w /var/lib/opencuda ]]; then
        RESULT_ROOT=/var/lib/opencuda/results
    else
        RESULT_ROOT=/tmp/opencuda-results
    fi
    mkdir -p "$RESULT_ROOT"
}

initialize_run() {
    find_result_root
    local stamp
    stamp="$(date -u +'%Y%m%dT%H%M%SZ')"
    RUN_DIR="$RESULT_ROOT/$stamp"
    mkdir -p "$RUN_DIR"
    REPORT="$RUN_DIR/report.md"
    EVENT_LOG="$RUN_DIR/events.log"
    TELEMETRY="$RUN_DIR/nvidia-telemetry.csv"
    ABORT_FILE="$RUN_DIR/LOAD_ABORTED"
    {
        printf '# openCUDA DL380p/CUBIX live-USB report\n\n'
        printf -- "- Scanner version: \`%s\`\n" "$SCAN_VERSION"
        printf -- "- Started: \`%s\`\n" "$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
        printf -- '- Expected components: CUBIX Desktop Elite; CUBIX 400-A07994 HIC; three NVIDIA Tesla K80 900-22080-6300-000 boards; NVIDIA Quadro 6000 host display GPU; Intel Xeon Phi 5110P\n'
    } >"$REPORT"
    : >"$EVENT_LOG"
    log "Results directory: $RUN_DIR"
}

connect_wifi() {
    if ! command -v nmcli >/dev/null 2>&1; then
        log "NetworkManager/nmcli is unavailable; results will remain on the USB"
        return 1
    fi
    nmcli radio wifi on >/dev/null 2>&1 || true
    printf '\nAvailable Wi-Fi networks:\n'
    nmcli --colors no --fields IN-USE,SSID,SIGNAL,SECURITY device wifi list || true
    local ssid
    read -r -p 'Wi-Fi SSID: ' ssid
    [[ -n "$ssid" ]] || return 1
    printf 'NetworkManager will now request the Wi-Fi secret.\n'
    if nmcli --ask --wait 45 device wifi connect "$ssid"; then
        WIFI_CONNECTION="$ssid"
        log "Wi-Fi connected"
        return 0
    fi
    log "Wi-Fi connection failed"
    return 1
}

capture_inventory() {
    capture "Kernel" uname -a
    capture "Operating system" sh -c 'cat /etc/os-release'
    capture "CPU" lscpu
    capture "NUMA" numactl --hardware
    capture "DMI (sanitized)" dmidecode
    capture "PCIe tree" lspci -tv
    capture "PCIe inventory and drivers" lspci -nnk
    capture "PCIe capabilities and negotiated links" lspci -nnvvv
    capture "USB inventory" lsusb -v
    capture "Storage models" lsblk -o NAME,TYPE,SIZE,MODEL,TRAN,HCTL
    capture "Network device state" nmcli -t -f DEVICE,TYPE,STATE device status
    capture "Loaded modules" lsmod
    capture "Kernel command line" sh -c 'cat /proc/cmdline'
    capture "Kernel log" dmesg --color=never
    capture "HPE/IPMI controller" ipmitool mc info
    capture "HPE/IPMI sensors" ipmitool sdr elist
    capture "HPE/IPMI event log" ipmitool sel elist
    capture "Hardware sensors" sensors -A
}

capture_nvidia() {
    capture "NVIDIA device list" nvidia-smi -L
    capture "NVIDIA detailed state" nvidia-smi -q
    capture "NVIDIA topology" nvidia-smi topo -m
    capture "NVIDIA PCIe and thermal summary" nvidia-smi \
        --query-gpu=index,name,pci.bus_id,pci.link.gen.current,pci.link.width.current,temperature.gpu,power.draw,pstate,clocks.current.sm,ecc.errors.uncorrected.volatile.total \
        --format=csv
}

compile_load_helper() {
    local script_dir source output
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    source="$script_dir/k80_staged_load.cu"
    output="$RUN_DIR/k80_staged_load"
    if [[ -x "$script_dir/k80_staged_load" ]]; then
        printf '%s\n' "$script_dir/k80_staged_load"
        return 0
    fi
    if [[ ! -f "$source" ]] || ! command -v nvcc >/dev/null 2>&1; then
        return 1
    fi
    nvcc -O2 -std=c++14 -arch=sm_37 -Xcompiler=-pthread "$source" -o "$output" >>"$EVENT_LOG" 2>&1 || return 1
    printf '%s\n' "$output"
}

monitor_temperature() {
    if [[ ! -s "$TELEMETRY" ]]; then
        printf 'stage,timestamp,index,pci.bus_id,temperature.gpu,power.draw,utilization.gpu,pstate,clocks.current.sm,ecc.errors.uncorrected.volatile.total\n' >"$TELEMETRY"
    fi
    while :; do
        local sample temperatures temperature
        sample="$(nvidia-smi --query-gpu=timestamp,index,pci.bus_id,temperature.gpu,power.draw,utilization.gpu,pstate,clocks.current.sm,ecc.errors.uncorrected.volatile.total --format=csv,noheader,nounits 2>/dev/null)" || {
            printf 'nvidia-smi telemetry failure\n' >"$ABORT_FILE"
            break
        }
        while IFS= read -r sample_line; do
            printf '%s,%s\n' "$CURRENT_STAGE" "$sample_line" >>"$TELEMETRY"
        done <<<"$sample"
        temperatures="$(printf '%s\n' "$sample" | awk -F',' '{gsub(/ /,"",$4); print $4}')"
        while IFS= read -r temperature; do
            if [[ "$temperature" =~ ^[0-9]+$ ]] && (( temperature >= ABORT_TEMP_C )); then
                printf 'temperature reached %s C (limit %s C)\n' "$temperature" "$ABORT_TEMP_C" >"$ABORT_FILE"
                return
            fi
        done <<<"$temperatures"
        sleep 1
    done
}

run_load_stage() {
    local label="$1" seconds="$2" duty="$3" helper="$4"
    log "Starting $label stage: ${seconds}s at ${duty}% duty"
    CURRENT_STAGE="$label"
    rm -f "$ABORT_FILE"
    monitor_temperature &
    MONITOR_PID=$!
    "$helper" --seconds "$seconds" --duty "$duty" --memory-mib "$MEMORY_MIB" \
        --devices "$K80_DEVICE_LIST" >>"$EVENT_LOG" 2>&1 &
    LOAD_PID=$!
    while kill -0 "$LOAD_PID" 2>/dev/null; do
        if [[ -s "$ABORT_FILE" ]]; then
            log "Aborting $label: $(<"$ABORT_FILE")"
            kill "$LOAD_PID" 2>/dev/null || true
            wait "$LOAD_PID" 2>/dev/null || true
            LOAD_PID=""
            kill "$MONITOR_PID" 2>/dev/null || true
            wait "$MONITOR_PID" 2>/dev/null || true
            MONITOR_PID=""
            return 1
        fi
        sleep 1
    done
    wait "$LOAD_PID"
    local status=$?
    LOAD_PID=""
    kill "$MONITOR_PID" 2>/dev/null || true
    wait "$MONITOR_PID" 2>/dev/null || true
    MONITOR_PID=""
    (( status == 0 )) || return "$status"
    log "Completed $label stage"
}

run_staged_test() {
    if ! command -v nvidia-smi >/dev/null 2>&1 || ! nvidia-smi >/dev/null 2>&1; then
        log "NVIDIA driver unavailable; refusing GPU load"
        return 1
    fi
    local gpu_count k80_count helper confirmation
    gpu_count="$(nvidia-smi --query-gpu=index --format=csv,noheader 2>/dev/null | wc -l)"
    K80_DEVICE_LIST="$(nvidia-smi --query-gpu=index,name --format=csv,noheader 2>/dev/null | \
        awk -F',' 'tolower($2) ~ /tesla k80/ {gsub(/ /,"",$1); printf "%s%s", separator, $1; separator=","}')"
    if [[ -z "$K80_DEVICE_LIST" ]]; then
        log "No device identified by the NVIDIA driver as Tesla K80; refusing GPU load"
        return 1
    fi
    k80_count="$(awk -F',' '{print NF}' <<<"$K80_DEVICE_LIST")"
    printf '\nDetected %s logical NVIDIA device(s), including %s Tesla K80 GK210 device(s).\n' "$gpu_count" "$k80_count"
    printf 'Only K80 indexes [%s] will be loaded; the Quadro display GPU is excluded.\n' "$K80_DEVICE_LIST"
    printf 'Expected: 2 logical devices per installed Tesla K80. Verify the physical card count before proceeding.\n'
    if (( k80_count != EXPECTED_K80_DEVICES )); then
        log "Detected $k80_count K80 logical devices; this qualification run requires exactly $EXPECTED_K80_DEVICES"
        log "Inventory is retained, but load is refused. Install one K80 for the initial test or explicitly change OPENCUDA_EXPECTED_K80_DEVICES for a later approved configuration"
        return 1
    fi
    printf 'The K80 is passive. A staged load without verified forced airflow can damage hardware.\n'
    read -r -p 'Type VERIFIED-FORCED-AIRFLOW to enable load testing: ' confirmation
    if [[ "$confirmation" != "VERIFIED-FORCED-AIRFLOW" ]]; then
        log "Operator declined or failed the forced-airflow gate; load skipped"
        return 1
    fi
    helper="$(compile_load_helper)" || {
        log "CUDA load helper unavailable; nvcc and an R470-compatible CUDA runtime are required"
        return 1
    }
    log "Software abort threshold: ${ABORT_TEMP_C} C; NVIDIA hardware protection remains enabled"
    log "Idle observation: ${IDLE_SECONDS}s"
    CURRENT_STAGE="idle"
    rm -f "$ABORT_FILE"
    monitor_temperature &
    MONITOR_PID=$!
    local waited=0
    while (( waited < IDLE_SECONDS )); do
        [[ ! -s "$ABORT_FILE" ]] || break
        sleep 1
        ((waited += 1))
    done
    kill "$MONITOR_PID" 2>/dev/null || true
    wait "$MONITOR_PID" 2>/dev/null || true
    MONITOR_PID=""
    [[ ! -s "$ABORT_FILE" ]] || return 1
    run_load_stage "partial-load" "$PARTIAL_SECONDS" 25 "$helper" || return 1
    run_load_stage "full-load" "$FULL_SECONDS" 100 "$helper" || return 1
    return 0
}

package_results() {
    {
        printf "\n- Finished: \`%s\`\n" "$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
        printf -- "- Final status: \`%s\`\n" "$FINAL_STATUS"
    } >>"$REPORT"
    local archive="$RUN_DIR/opencuda-scan-results.tar.gz"
    local archive_tmp
    archive_tmp="$(mktemp "$RESULT_ROOT/.opencuda-results.XXXXXX.tar.gz")"
    if ! tar -C "$RUN_DIR" -czf "$archive_tmp" .; then
        rm -f "$archive_tmp"
        return 1
    fi
    mv "$archive_tmp" "$archive"
    printf '%s\n' "$archive"
}

send_gmail() {
    local archive="$1" gmail app_password attachment boundary mail_file curl_config
    read -r -p 'Gmail address (report sends to the same account): ' gmail
    [[ "$gmail" =~ ^[^[:space:]@]+@[^[:space:]@]+\.[^[:space:]@]+$ ]] || {
        log "Invalid Gmail address; email skipped"
        return 1
    }
    read -r -s -p 'Gmail app password: ' app_password
    printf '\n'
    app_password="${app_password// /}"
    [[ -n "$app_password" ]] || return 1
    attachment="$archive"
    if (( $(stat -c '%s' "$archive") > 18000000 )); then
        attachment="$REPORT"
        log "Archive exceeds safe Gmail attachment size; emailing report only"
    fi
    boundary="opencuda-$(date +%s)-$$"
    mail_file="$(mktemp /tmp/opencuda-mail.XXXXXX)"
    curl_config="$(mktemp /tmp/opencuda-curl.XXXXXX)"
    chmod 600 "$mail_file" "$curl_config"
    {
        printf 'From: %s\r\n' "$gmail"
        printf 'To: %s\r\n' "$gmail"
        printf 'Subject: openCUDA DL380p/CUBIX scan %s\r\n' "$FINAL_STATUS"
        printf 'MIME-Version: 1.0\r\n'
        printf 'Content-Type: multipart/mixed; boundary="%s"\r\n\r\n' "$boundary"
        printf -- '--%s\r\nContent-Type: text/plain; charset=utf-8\r\n\r\n' "$boundary"
        printf 'Scan status: %s\r\nResults remain on the OPENCUDA_DATA partition.\r\n\r\n' "$FINAL_STATUS"
        printf -- '--%s\r\n' "$boundary"
        printf 'Content-Type: application/octet-stream; name="%s"\r\n' "$(basename "$attachment")"
        printf 'Content-Transfer-Encoding: base64\r\n'
        printf 'Content-Disposition: attachment; filename="%s"\r\n\r\n' "$(basename "$attachment")"
        base64 -w 76 "$attachment"
        printf '\r\n--%s--\r\n' "$boundary"
    } >"$mail_file"
    {
        printf 'url = "smtps://smtp.gmail.com:465"\n'
        printf 'ssl-reqd\n'
        printf 'user = "%s:%s"\n' "$gmail" "$app_password"
        printf 'mail-from = "%s"\n' "$gmail"
        printf 'mail-rcpt = "%s"\n' "$gmail"
        printf 'upload-file = "%s"\n' "$mail_file"
        printf 'silent\nshow-error\nfail\n'
    } >"$curl_config"
    app_password=""
    if curl --config "$curl_config"; then
        log "Gmail delivery succeeded"
        rm -f "$curl_config" "$mail_file"
        return 0
    fi
    log "Gmail delivery failed; results remain at $RUN_DIR"
    rm -f "$curl_config" "$mail_file"
    return 1
}

main() {
    initialize_run
    if (( EUID != 0 )); then
        log "Run as root to capture DMI, IPMI, PCIe capabilities, and kernel logs"
    fi
    connect_wifi || true
    capture_inventory
    capture_nvidia
    if run_staged_test; then
        FINAL_STATUS="PASS"
    else
        FINAL_STATUS="INVENTORY_COMPLETE_LOAD_NOT_QUALIFIED"
    fi
    capture "Post-test NVIDIA state" nvidia-smi -q
    capture "Post-test kernel error extract" sh -c "dmesg | grep -Ei 'NVRM|Xid|AER|PCIe|IOMMU|EDAC|ECC|thermal|overheat' || true"
    local archive
    if ! archive="$(package_results)"; then
        log "Result packaging failed; uncompressed results remain at $RUN_DIR"
        printf '\nScan incomplete: result packaging failed\nResults: %s\n' "$RUN_DIR"
        return 1
    fi
    send_gmail "$archive" || true
    printf '\nScan complete: %s\nResults: %s\n' "$FINAL_STATUS" "$RUN_DIR"
}

main "$@"
