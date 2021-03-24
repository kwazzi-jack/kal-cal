from importlib import import_module
import pytest

def import_attributes(module):
    attributes = dir(module)
    for attribute in attributes:
        getattr(module, attribute)
        

def import_modules_list(imports):
    for level in imports:
        try:
            mod = import_module("kalcal." + level)
            import_attributes(mod)
        except:
            return False

    return True


def test_import_datasets():
    levels = [
        "datasets",
        "datasets.antenna_tables",
        "datasets.gains",
        "datasets.ms",
        "datasets.sky_models"
    ]

    assert import_modules_list(levels)


def test_import_examples():
    levels = [
        "examples"
    ]

    assert import_modules_list(levels)


def test_import_filters():
    levels = [
        "filters",
        "filters.ekf",
        "filters.iekf"
    ]

    assert import_modules_list(levels)


def test_import_generation():
    levels = [
        "generation",
        "generation.create_ms",
        "generation.from_ms",
        "generation.loader",
        "generation.normal_gains",
        "generation.parser",
        "generation.phase_gains"
    ]

    assert import_modules_list(levels)


def test_import_plotting():
    levels = [
        "plotting",
        "plotting.multiplot",
        "plotting.plotops",
        "plotting.singleplot"
    ]

    assert import_modules_list(levels)


def test_import_smoothers():
    levels = [
        "smoothers",
        "smoothers.eks"
    ]

    assert import_modules_list(levels)


def test_import_tools():
    levels = [
        "tools",
        "tools.jacobian",
        "tools.sparseops",
        "tools.statistics",
        "tools.utils"
    ]

    assert import_modules_list(levels)


def test_import_tuners():
    levels = [
        "tuners",
        "tuners.equations"
    ]

    assert import_modules_list(levels)