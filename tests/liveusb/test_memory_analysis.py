#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

REPO_ROOT = Path(__file__).resolve().parents[2]
ANALYZER_PATH = REPO_ROOT / "scripts" / "liveusb" / "analyze_memory.py"
SPEC = importlib.util.spec_from_file_location("analyze_memory", ANALYZER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to load memory analyzer")
ANALYZER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = ANALYZER
SPEC.loader.exec_module(ANALYZER)


def fixture(socket_counts: tuple[int, int] = (4, 4), second_size_gib: int = 16) -> str:
    sections = [
        """Handle 0x0001, DMI type 1, 27 bytes
System Information
    Manufacturer: HP
    Product Name: ProLiant DL380p Gen8
""",
        """Handle 0x0004, DMI type 4, 42 bytes
Processor Information
    Socket Designation: Proc 1
    Version: Intel(R) Xeon(R) CPU E5-2620 0 @ 2.00GHz
""",
        """Handle 0x0005, DMI type 4, 42 bytes
Processor Information
    Socket Designation: Proc 2
    Version: Intel(R) Xeon(R) CPU E5-2620 0 @ 2.00GHz
""",
        """Handle 0x0010, DMI type 16, 23 bytes
Physical Memory Array
    Maximum Capacity: 768 GB
    Error Correction Type: Multi-bit ECC
    Number Of Devices: 24
""",
    ]
    handle = 0x20
    letter_to_slot = {"A": 12, "B": 9, "C": 1, "D": 4}
    for socket, count in enumerate(socket_counts, start=1):
        for index, letter in enumerate("ABCD"[:count]):
            size_gib = second_size_gib if socket == 2 else 16
            sections.append(
                f"""Handle 0x{handle:04X}, DMI type 17, 40 bytes
Memory Device
    Size: {size_gib} GB
    Locator: PROC {socket} DIMM {letter_to_slot[letter]}
    Bank Locator: CHANNEL {index}
    Type: DDR3
    Type Detail: Synchronous Registered (Buffered)
    Speed: 1333 MT/s
    Total Width: 72 bits
    Data Width: 64 bits
    Manufacturer: HPE
    Serial Number: DO-NOT-REPORT-{socket}-{letter}
    Part Number: TEST-16GB-RDIMM
    Rank: 2
    Configured Memory Speed: 1333 MT/s
    Configured Voltage: 1.35 V
"""
            )
            handle += 1
    return "\n".join(sections)


class MemoryAnalysisTests(unittest.TestCase):
    def render(self, text: str) -> str:
        return ANALYZER.render_report(ANALYZER.parse_records(text))

    def test_balanced_eight_dimm_configuration(self) -> None:
        report = self.render(fixture())
        self.assertIn("Installed memory: 128 GiB across 8/24 slots", report)
        self.assertIn("CPU memory-speed ceiling: 1333 MT/s", report)
        self.assertIn("Configured voltages: 1.35 V", report)
        self.assertIn("Memory-array ECC: Multi-bit ECC", report)
        self.assertIn("64+8", report)
        self.assertIn("Two-socket balance: PASS", report)
        self.assertIn("Population order: PASS", report)
        self.assertIn("Rank placement: PASS", report)
        self.assertIn("LRDIMM: 768 GiB", report)
        self.assertIn("Capacity-first: 24 identical 32 GiB LRDIMMs", report)
        self.assertNotIn("DO-NOT-REPORT", report)

    def test_unbalanced_socket_capacity_is_flagged(self) -> None:
        report = self.render(fixture(second_size_gib=8))
        self.assertIn("Two-socket balance: ATTENTION", report)
        self.assertIn("P1 64 GiB/4 DIMMs; P2 32 GiB/4 DIMMs", report)

    def test_missing_paired_slots_is_flagged(self) -> None:
        report = self.render(fixture(socket_counts=(4, 2)))
        self.assertIn("Two-socket balance: ATTENTION", report)
        self.assertIn("Population order: ATTENTION", report)


if __name__ == "__main__":
    unittest.main()
