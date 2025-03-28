"""Tests for the VEExperiment class."""

from itertools import product
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

import numpy as np
import pytest

from snakemake_helper import VEExperiment
from snakemake_helper.ve_experiment import _get_outpath_with_wildcards

PARAMS: dict = {
    "b": {"c": {"param": range(2, 4)}},
    "a": {"param": range(2)},
}
"""Parameters to vary between runs.

NB: Deliberately not in alphabetical order, as params should be sorted.
"""
OUTPUT_FILES = (
    "vr_full_model_configuration.toml",
    "initial_state.nc",
    "final_state.nc",
    "all_continuous_data.nc",
    "ve_run.log",
)


def test_get_outpath_with_wildcards() -> None:
    """Test the _get_outpath_with_wildcards() function."""
    assert Path(
        _get_outpath_with_wildcards("out", ("core.param1", "core.param2"))
    ) == Path("out/core.param1_{core_param1}/core.param2_{core_param2}")


@pytest.fixture
def ve_exp():
    """Return a VEExperiment."""
    return VEExperiment("out", PARAMS)


def test_outpath(ve_exp: VEExperiment) -> None:
    """Test the outpath property."""
    assert Path(ve_exp.outpath) == Path("out/a.param_{a_param}/b.c.param_{b_c_param}")


def test_output(ve_exp: VEExperiment) -> None:
    """Test the output property."""
    outpath = Path("out/a.param_{a_param}/b.c.param_{b_c_param}")

    expected = np.array(sorted(str(outpath / file) for file in OUTPUT_FILES))
    actual = np.array(sorted(ve_exp.output))
    assert (expected == actual).all()


def test_all_outputs(ve_exp: VEExperiment) -> None:
    """Test the all_outputs property."""
    outpaths = [
        Path(f"out/a.param_{a}/b.c.param_{b}")
        for a, b in product(PARAMS["a"]["param"], PARAMS["b"]["c"]["param"])
    ]

    expected = np.array(
        sorted(str(dir / file) for dir, file in product(outpaths, OUTPUT_FILES))
    )
    actual = np.array(sorted(ve_exp.all_outputs))
    assert (expected == actual).all()


@patch("snakemake_helper.ve_experiment.ve_run")
def test_run(ve_run_mock: Mock, ve_exp: VEExperiment) -> None:
    """Test the run() method invokes ve_run() correctly."""
    params: dict[str, dict[str, Any]] = {
        "a": {"param": 1},
        "b": {"c": {"param": 2}},
    }
    outpath = Path(
        f"out/a.param_{params['a']['param']}/b.c.param_{params['b']['c']['param']}"
    )

    # Params also needs to include the output path
    params |= {"core": {"data_output_options": {"out_path": str(outpath)}}}

    input = ("dataset",)
    output = [str(outpath / file) for file in OUTPUT_FILES]
    ve_exp.run(input, output)
    ve_run_mock.assert_called_once_with(
        cfg_paths=input,
        override_params=params,
        logfile=outpath / "ve_run.log",
    )


@patch("snakemake_helper.ve_experiment.ve_run")
def test_run_bad_input(ve_run_mock: Mock, ve_exp: VEExperiment) -> None:
    """Test the run() method raises an error if the outputs are unknown."""
    outpath = Path("out/a.param_1/b.c.param_2")
    outputs = (str(outpath / file) for file in OUTPUT_FILES)

    # File in unknown folder
    with pytest.raises(RuntimeError):
        ve_exp.run(("dataset",), (*outputs, f"another/folder/{OUTPUT_FILES[0]}"))

    # Unknown file in known folder
    with pytest.raises(RuntimeError):
        ve_exp.run(("dataset",), (*outputs, str(outpath / "unknown_file.txt")))


@patch("snakemake_helper.ve_experiment.ve_run")
def test_run_overlapping_params(ve_run_mock: Mock) -> None:
    """Test the run() method invokes ve_run() correctly when config options overlap.

    The parameter dicts have to be recursively merged in order not to clobber sub-dicts.
    """
    all_params: dict[str, dict[str, Any]] = {
        "a": {"param": range(2)},
        "core": {"b": {"param": range(2)}},
    }
    exp = VEExperiment("out", all_params)
    params: dict[str, dict[str, Any]] = {
        "a": {"param": 0},
        "core": {"b": {"param": 1}},
    }
    outpath = Path(
        f"out/a.param_{params['a']['param']}/"
        f"core.b.param_{params['core']['b']['param']}"
    )

    # Params also needs to include the output path
    params["core"] |= {"data_output_options": {"out_path": str(outpath)}}

    input = ("dataset",)
    output = [str(outpath / file) for file in OUTPUT_FILES]
    exp.run(input, output)
    ve_run_mock.assert_called_once_with(
        cfg_paths=input,
        override_params=params,
        logfile=outpath / "ve_run.log",
    )


@patch("snakemake_helper.ve_experiment.ve_run")
def test_run_outpath_set_twice(ve_run_mock: Mock) -> None:
    """Test the run() method raises an error if the outpath is set twice.

    It can't be set as a config option.
    """
    all_params: dict[str, dict[str, Any]] = {
        "a": {"param": range(2)},
        "core": {"data_output_options": {"out_path": ("something",)}},
    }
    exp = VEExperiment("out", all_params)
    params: dict[str, dict[str, Any]] = {
        "a": {"param": 0},
        "core": {"data_output_options": {"out_path": ("something",)}},
    }
    outpath = Path(
        f"out/a.param_{params['a']['param']}/"
        "core.data_output_options.out_path_something"
    )

    # Params also needs to include the output path
    params["core"] = {"data_output_options": {"out_path": str(outpath)}}

    input = ("dataset",)
    output = [str(outpath / file) for file in OUTPUT_FILES]
    with pytest.raises(RuntimeError):
        exp.run(input, output)
