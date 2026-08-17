from opencuda import Capability, runtime_info


def test_runtime_info_is_populated() -> None:
    info = runtime_info()
    assert info.system
    assert info.machine
    assert info.python


def test_capability_values_are_stable() -> None:
    assert Capability.NATIVE.value == "native"
    assert Capability.UNSUPPORTED.value == "unsupported"
