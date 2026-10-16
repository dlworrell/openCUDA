#!/usr/bin/env python3
"""Analyze DL380p Gen8 SMBIOS memory data without network access."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

HPE_QUICKSPECS = "c04123238, version 72 (2015-09-28)"
TOTAL_SLOTS = 24
SLOTS_PER_SOCKET = 12
CHANNELS_PER_SOCKET = 4
SLOT_NUMBER_TO_LETTER = {
    1: "C",
    2: "G",
    3: "K",
    4: "D",
    5: "H",
    6: "L",
    7: "J",
    8: "F",
    9: "B",
    10: "I",
    11: "E",
    12: "A",
}
LETTER_TO_CHANNEL_POSITION = {
    letter: (channel, position)
    for channel, letters in enumerate(("AEI", "BFJ", "CGK", "DHL"), start=1)
    for position, letter in enumerate(letters, start=1)
}


@dataclass(frozen=True)
class DmiRecord:
    type_number: int
    title: str
    fields: dict[str, str]


@dataclass(frozen=True)
class Dimm:
    locator: str
    bank_locator: str
    size_mib: int
    technology: str
    type_detail: str
    rated_mts: int | None
    configured_mts: int | None
    manufacturer: str
    part_number: str
    rank: str
    configured_voltage: str
    total_width_bits: int | None
    data_width_bits: int | None
    socket: int | None
    slot_letter: str | None


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Report DL380p Gen8 DIMM inventory, balance, and capacity options."
    )
    parser.add_argument(
        "--dmidecode-file",
        type=Path,
        help="Read saved dmidecode text instead of interrogating the current host.",
    )
    return parser.parse_args()


def read_dmidecode(path: Path | None) -> str:
    if path is not None:
        return path.read_text(encoding="utf-8")
    try:
        completed = subprocess.run(
            ["dmidecode", "--type", "1,4,16,17"],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("dmidecode is unavailable") from exc
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.strip() or f"exit status {exc.returncode}"
        raise RuntimeError(f"dmidecode failed: {detail}") from exc
    return completed.stdout


def parse_records(text: str) -> list[DmiRecord]:
    records: list[DmiRecord] = []
    current_type: int | None = None
    title = ""
    fields: dict[str, str] = {}

    def finish() -> None:
        nonlocal current_type, title, fields
        if current_type is not None:
            records.append(DmiRecord(current_type, title, fields))
        current_type = None
        title = ""
        fields = {}

    for raw_line in text.splitlines():
        handle = re.match(r"^Handle\s+\S+,\s+DMI type (\d+),", raw_line)
        if handle:
            finish()
            current_type = int(handle.group(1))
            continue
        if current_type is None:
            continue
        line = raw_line.strip()
        if not line:
            continue
        if not title and ":" not in line:
            title = line
            continue
        field = re.match(r"^([^:]+):\s*(.*)$", line)
        if field and field.group(1) not in fields:
            fields[field.group(1)] = field.group(2).strip()
    finish()
    return records


def parse_size_mib(value: str) -> int:
    match = re.fullmatch(r"(\d+)\s*(KB|MB|GB|TB)", value.strip(), re.IGNORECASE)
    if not match:
        return 0
    amount = int(match.group(1))
    factors = {"KB": 1 / 1024, "MB": 1, "GB": 1024, "TB": 1024 * 1024}
    return int(amount * factors[match.group(2).upper()])


def parse_speed(value: str) -> int | None:
    match = re.search(r"(\d+)\s*(?:MT/s|MHz)", value, re.IGNORECASE)
    return int(match.group(1)) if match else None


def parse_width(value: str) -> int | None:
    match = re.search(r"(\d+)\s*bits?", value, re.IGNORECASE)
    return int(match.group(1)) if match else None


def socket_from_locator(locator: str) -> int | None:
    patterns = (
        r"\bPROC(?:ESSOR)?\s*([12])\b",
        r"\bCPU\s*([12])\b",
        r"\bP([12])[-_ ]",
    )
    for pattern in patterns:
        match = re.search(pattern, locator, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return None


def slot_letter_from_locator(locator: str) -> str | None:
    match = re.search(r"\bDIMM[-_ ]*([A-L])(?:\d|\b)", locator, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    numeric = re.search(r"\bDIMM[-_ ]*(\d{1,2})\b", locator, re.IGNORECASE)
    return SLOT_NUMBER_TO_LETTER.get(int(numeric.group(1))) if numeric else None


def technology_from_fields(memory_type: str, detail: str) -> str:
    combined = f"{memory_type} {detail}".lower().replace("-", " ")
    if "load reduced" in combined or "lrdimm" in combined:
        return "LRDIMM"
    if "unbuffered" in combined or "udimm" in combined:
        return "UDIMM"
    if "hypercloud" in combined or "hdimm" in combined:
        return "HDIMM"
    if "registered" in combined or "buffered" in combined or "rdimm" in combined:
        return "Registered/buffered"
    return memory_type or "Unknown"


def dimms_from_records(records: list[DmiRecord]) -> list[Dimm]:
    dimms: list[Dimm] = []
    for record in records:
        if record.type_number != 17:
            continue
        fields = record.fields
        size_mib = parse_size_mib(fields.get("Size", ""))
        if size_mib <= 0:
            continue
        locator = fields.get("Locator", "Unknown")
        detail = fields.get("Type Detail", "Unknown")
        memory_type = fields.get("Type", "Unknown")
        dimms.append(
            Dimm(
                locator=locator,
                bank_locator=fields.get("Bank Locator", "Unknown"),
                size_mib=size_mib,
                technology=technology_from_fields(memory_type, detail),
                type_detail=detail,
                rated_mts=parse_speed(fields.get("Speed", "")),
                configured_mts=parse_speed(
                    fields.get(
                        "Configured Memory Speed",
                        fields.get("Configured Clock Speed", ""),
                    )
                ),
                manufacturer=fields.get("Manufacturer", "Unknown"),
                part_number=fields.get("Part Number", "Unknown").strip(),
                rank=fields.get("Rank", "Unknown"),
                configured_voltage=fields.get("Configured Voltage", "Unknown"),
                total_width_bits=parse_width(fields.get("Total Width", "")),
                data_width_bits=parse_width(fields.get("Data Width", "")),
                socket=socket_from_locator(locator),
                slot_letter=slot_letter_from_locator(locator),
            )
        )
    return dimms


def processor_versions(records: list[DmiRecord]) -> list[str]:
    return [
        record.fields["Version"]
        for record in records
        if record.type_number == 4 and record.fields.get("Version")
    ]


def platform_name(records: list[DmiRecord]) -> str:
    for record in records:
        if record.type_number == 1 and record.fields.get("Product Name"):
            return record.fields["Product Name"]
    return "Unknown"


def array_ecc_type(records: list[DmiRecord]) -> str:
    for record in records:
        if record.type_number == 16 and record.fields.get("Error Correction Type"):
            return record.fields["Error Correction Type"]
    return "unknown"


def cpu_memory_limit(processors: list[str]) -> int | None:
    normalized = " ".join(processors).lower()
    if re.search(r"\be5-2620\s+v2\b", normalized):
        return 1600
    if re.search(r"\be5-2620\b", normalized):
        return 1333
    return None


def format_gib(size_mib: int) -> str:
    size_gib = size_mib / 1024
    return f"{size_gib:.0f} GiB" if size_gib.is_integer() else f"{size_gib:.1f} GiB"


def distinct(values: list[str | int | None]) -> str:
    cleaned = sorted({str(value) for value in values if value not in {None, "", "Unknown"}})
    return ", ".join(cleaned) if cleaned else "unknown"


def report_balance(dimms: list[Dimm]) -> tuple[str, list[str]]:
    notes: list[str] = []
    if any(dimm.socket not in {1, 2} for dimm in dimms):
        return "UNVERIFIED", ["SMBIOS slot locators do not identify both processor sockets."]
    socket_sizes = {
        socket: sum(dimm.size_mib for dimm in dimms if dimm.socket == socket)
        for socket in (1, 2)
    }
    socket_counts = {socket: sum(dimm.socket == socket for dimm in dimms) for socket in (1, 2)}
    if socket_sizes[1] != socket_sizes[2] or socket_counts[1] != socket_counts[2]:
        notes.append(
            "Socket totals differ: "
            f"P1 {format_gib(socket_sizes[1])}/{socket_counts[1]} DIMMs; "
            f"P2 {format_gib(socket_sizes[2])}/{socket_counts[2]} DIMMs."
        )
        return "ATTENTION", notes
    notes.append(
        f"P1 and P2 each contain {format_gib(socket_sizes[1])} across "
        f"{socket_counts[1]} DIMMs."
    )

    by_letter: dict[str, list[Dimm]] = {}
    for dimm in dimms:
        if dimm.slot_letter:
            by_letter.setdefault(dimm.slot_letter, []).append(dimm)
    if len(by_letter) == len(dimms) // 2 and all(len(items) == 2 for items in by_letter.values()):
        for letter, items in sorted(by_letter.items()):
            sockets = {item.socket for item in items}
            capacities = {item.size_mib for item in items}
            if sockets != {1, 2} or len(capacities) != 1:
                notes.append(f"Paired slot {letter} is not symmetric across P1 and P2.")
                return "ATTENTION", notes
    else:
        notes.append("Per-channel symmetry could not be proven from SMBIOS slot lettering.")
        return "PARTIAL", notes
    return "PASS", notes


def report_population_order(dimms: list[Dimm]) -> tuple[str, str]:
    if any(dimm.slot_letter is None or dimm.socket not in {1, 2} for dimm in dimms):
        return "UNVERIFIED", "SMBIOS does not expose a usable A-L slot letter for every DIMM."
    socket_letters = {
        socket: {dimm.slot_letter for dimm in dimms if dimm.socket == socket}
        for socket in (1, 2)
    }
    if socket_letters[1] != socket_letters[2]:
        return "ATTENTION", (
            f"P1 positions {','.join(sorted(socket_letters[1]))} and "
            f"P2 positions {','.join(sorted(socket_letters[2]))} are not paired."
        )
    letters = socket_letters[1]
    expected = set("ABCDEFGHIJKL"[: len(letters)])
    if letters == expected:
        return "PASS", f"Populated paired positions are sequential A through {max(letters)}."
    return "ATTENTION", (
        f"Detected slot letters {','.join(sorted(letters))}; expected the first "
        f"{len(letters)} sequential positions {','.join(sorted(expected))}."
    )


def report_rank_placement(dimms: list[Dimm]) -> tuple[str, str]:
    groups: dict[tuple[int, int], list[tuple[int, int]]] = {}
    unresolved = False
    for dimm in dimms:
        if dimm.socket not in {1, 2} or dimm.slot_letter not in LETTER_TO_CHANNEL_POSITION:
            unresolved = True
            continue
        rank_match = re.search(r"\d+", dimm.rank)
        if not rank_match:
            unresolved = True
            continue
        channel, position = LETTER_TO_CHANNEL_POSITION[dimm.slot_letter]
        groups.setdefault((dimm.socket, channel), []).append((position, int(rank_match.group())))
    for (socket, channel), placements in sorted(groups.items()):
        ranks = [rank for _, rank in sorted(placements)]
        if ranks != sorted(ranks, reverse=True):
            return "ATTENTION", (
                f"P{socket} channel {channel} does not place the highest-rank DIMM first."
            )
    if unresolved:
        return "PARTIAL", "One or more DIMM ranks or slot channels could not be resolved."
    return "PASS", "Within each populated channel, rank loading is heaviest to lightest."


def render_report(records: list[DmiRecord]) -> str:
    dimms = dimms_from_records(records)
    processors = processor_versions(records)
    total_mib = sum(dimm.size_mib for dimm in dimms)
    balance_status, balance_notes = report_balance(dimms) if dimms else ("UNAVAILABLE", [])
    order_status, order_note = (
        report_population_order(dimms) if dimms else ("UNAVAILABLE", "No populated DIMMs found.")
    )
    rank_status, rank_note = (
        report_rank_placement(dimms) if dimms else ("UNAVAILABLE", "No populated DIMMs found.")
    )
    cpu_limit = cpu_memory_limit(processors)

    lines = [
        "openCUDA DL380p Gen8 memory configuration analysis",
        f"Reference rules: HPE QuickSpecs {HPE_QUICKSPECS}",
        f"Platform reported by SMBIOS: {platform_name(records)}",
        f"Processors detected: {len(processors)}",
    ]
    lines.extend(f"  - {processor}" for processor in processors)
    lines.extend(
        [
            f"Installed memory: {format_gib(total_mib)} across {len(dimms)}/{TOTAL_SLOTS} slots",
            f"Detected technology: {distinct([dimm.technology for dimm in dimms])}",
            f"Rated DIMM speeds: {distinct([dimm.rated_mts for dimm in dimms])} MT/s",
            f"Configured speeds: {distinct([dimm.configured_mts for dimm in dimms])} MT/s",
            f"Configured voltages: {distinct([dimm.configured_voltage for dimm in dimms])}",
            f"Memory-array ECC: {array_ecc_type(records)}",
            f"CPU memory-speed ceiling: {cpu_limit or 'unresolved'} MT/s",
            f"Two-socket balance: {balance_status}",
        ]
    )
    lines.extend(f"  - {note}" for note in balance_notes)
    lines.extend(
        [
            f"Population order: {order_status}",
            f"  - {order_note}",
            f"Rank placement: {rank_status}",
            f"  - {rank_note}",
            "",
            "DIMM inventory:",
        ]
    )
    lines.append(
        "Socket | Slot | Size | Technology | Rated | Configured | Voltage | ECC width | "
        "Rank | Manufacturer | Part"
    )
    sorted_dimms = sorted(
        dimms, key=lambda item: (item.socket or 9, item.slot_letter or item.locator)
    )
    for dimm in sorted_dimms:
        lines.append(
            " | ".join(
                [
                    f"P{dimm.socket}" if dimm.socket else "?",
                    dimm.slot_letter or dimm.locator,
                    format_gib(dimm.size_mib),
                    dimm.technology,
                    f"{dimm.rated_mts} MT/s" if dimm.rated_mts else "unknown",
                    f"{dimm.configured_mts} MT/s" if dimm.configured_mts else "unknown",
                    dimm.configured_voltage,
                    (
                        f"{dimm.data_width_bits}+{dimm.total_width_bits - dimm.data_width_bits}"
                        if dimm.total_width_bits
                        and dimm.data_width_bits
                        and dimm.total_width_bits > dimm.data_width_bits
                        else "unresolved"
                    ),
                    dimm.rank,
                    dimm.manufacturer,
                    dimm.part_number,
                ]
            )
        )

    lines.extend(
        [
            "",
            "Recommended topology:",
            f"  - Two processors provide {CHANNELS_PER_SOCKET} channels and "
            f"{SLOTS_PER_SOCKET} slots per socket.",
            "  - Keep identical capacity, technology, rank, and part numbers paired across P1/P2.",
            "  - Populate P1-A, P2-A, P1-B, P2-B through P1-D, P2-D before E-H, then I-L.",
            "  - Eight identical DIMMs (four per processor) provide one DIMM per channel.",
            "  - Do not mix LRDIMM, RDIMM, UDIMM, or HDIMM technologies.",
            "",
            "Configuration targets:",
            "  - Minimum-load balanced baseline: 8 identical DIMMs, P1/P2 A-D, one DIMM "
            "per channel.",
            "  - Capacity-first: 24 identical 32 GiB LRDIMMs, P1/P2 A-L, 768 GiB total "
            "at 1066 MT/s.",
            "  - Published RDIMM capacity target: 24 identical 16 GiB RDIMMs, 384 GiB; "
            "three-DIMM-per-channel operation may reduce speed to 1066 MT/s.",
            "  - Preserve the installed DIMMs only when technology, rank, voltage, and "
            "part-number compatibility are confirmed.",
            "",
            "HPE-published platform ceilings:",
            "  - LRDIMM: 768 GiB (24 x 32 GiB at 1066 MT/s).",
            "  - HDIMM: 768 GiB (24 x 32 GiB at 1333 MT/s).",
            "  - RDIMM: 384 GiB (24 x 16 GiB at 1333 MT/s).",
            "  - UDIMM: 128 GiB (16 x 8 GiB; CPU and population may reduce speed).",
            "",
            "Interpretation:",
        ]
    )
    if balance_status == "PASS" and order_status == "PASS" and rank_status == "PASS":
        lines.append(
            "  - Installed memory is balanced and follows the observable population order."
        )
    else:
        lines.append(
            "  - Review ATTENTION or UNVERIFIED findings before purchasing or moving DIMMs."
        )
    if distinct([dimm.technology for dimm in dimms]) == "Registered/buffered":
        lines.append(
            "  - SMBIOS does not distinguish RDIMM from LRDIMM here; verify part numbers "
            "before choosing a capacity ceiling."
        )
    lines.append("  - Maximum capacity and maximum bandwidth are different design targets.")
    lines.append("  - DIMM serial numbers are intentionally excluded from this report.")
    return "\n".join(lines) + "\n"


def main() -> int:
    arguments = parse_arguments()
    try:
        text = read_dmidecode(arguments.dmidecode_file)
        records = parse_records(text)
    except (OSError, RuntimeError) as exc:
        print(f"Memory analysis unavailable: {exc}", file=sys.stderr)
        return 1
    if not any(record.type_number == 17 for record in records):
        print("Memory analysis unavailable: no SMBIOS Type 17 records", file=sys.stderr)
        return 1
    print(render_report(records), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
