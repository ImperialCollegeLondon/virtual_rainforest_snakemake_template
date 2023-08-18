"""Tests for the VRExperiment class."""
from itertools import product
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

import numpy as np
import pytest

from snakemake_helper import VRExperiment

PARAMS = {
    "a": {"param": range(2)},
    "b": {"c": {"param": range(2, 4)}},
}
OUTPUT_FILES = (
    "vr_full_model_configuration.toml",
    "initial_state.nc",
    "final_state.nc",
    "all_continuous_data.nc",
)


@pytest.fixture
def vr_exp():
    """A fixture providing a VRExperiment."""
    return VRExperiment("out", PARAMS)


def test_outpath(vr_exp: VRExperiment) -> None:
    """Test the outpath property."""
    assert Path(vr_exp.outpath) == Path("out/a.param_{a_param}/b.c.param_{b_c_param}")


def test_output(vr_exp: VRExperiment) -> None:
    """Test the output property."""
    outpath = Path("out/a.param_{a_param}/b.c.param_{b_c_param}")

    expected = np.array(sorted(str(outpath / file) for file in OUTPUT_FILES))
    actual = np.array(sorted(vr_exp.output))
    assert (expected == actual).all()


def test_all_outputs(vr_exp: VRExperiment) -> None:
    """Test the all_outputs property."""
    outpaths = [
        Path(f"out/a.param_{a}/b.c.param_{b}")
        for a, b in product(
            PARAMS["a"]["param"], PARAMS["b"]["c"]["param"]  # type: ignore
        )
    ]

    expected = np.array(
        sorted(str(dir / file) for dir, file in product(outpaths, OUTPUT_FILES))
    )
    actual = np.array(sorted(vr_exp.all_outputs))
    assert (expected == actual).all()


@patch("snakemake_helper.vr_experiment.vr_run")
def test_run_bad_input(vr_run_mock: Mock, vr_exp: VRExperiment) -> None:
    """Test the run() method raises an error if the outputs are unknown."""
    outpath = Path("out/a.param_1/b.c.param_2")
    outputs = (str(outpath / file) for file in OUTPUT_FILES)
    with pytest.raises(RuntimeError):
        vr_exp.run(("dataset",), (*outputs, "another/folder/file.txt"))


@patch("snakemake_helper.vr_experiment.vr_run")
def test_run(vr_run_mock: Mock, vr_exp: VRExperiment) -> None:
    """Test the run() method invokes vr_run() correctly."""
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
    vr_exp.run(input, output)
    vr_run_mock.assert_called_once_with(
        input, params, outpath / "vr_full_model_configuration.toml"
    )
