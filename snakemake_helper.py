"""Helper functionality for using Virtual Rainforest with Snakemake.

The main functionality for this module lies in the VRExperiment class, which represents
all the parameter sets which are being tested.
"""
from itertools import product
from pathlib import Path
from typing import Any, Iterable

from sklearn.model_selection import ParameterGrid
from snakemake.io import Namedlist
from virtual_rainforest.entry_points import vr_run


def _flatten_dict(d: dict[str, Any]) -> dict[str, Any]:
    """Flatten nested dicts into a single top-level dict.

    Subkeys are separated by dots.

    >>> _flatten_dict({'a': {'b': 1}})
    {'a.b': 1}
    """
    out: dict[str, Any] = {}
    for key, value in d.items():
        _flatten_dict_inner(value, out, key)
    return out


def _flatten_dict_inner(value: Any, out: dict[str, Any], key_prefix: str) -> None:
    """Helper function for _flatten_dict."""
    if isinstance(value, dict):
        for key2, value2 in value.items():
            _flatten_dict_inner(value2, out, f"{key_prefix}.{key2}")
    else:
        out[key_prefix] = value


def _unflatten_dict(d: dict[str, Any]) -> dict[str, Any]:
    """Performs the opposite operation to _flatten_dict.

    >>> _unflatten_dict({'a.b': 1})
    {'a': {'b': 1}}
    """
    out: dict[str, Any] = {}
    for key, value in d.items():
        key_parts = key.split(".")
        cur_dict = {key_parts.pop(): value}
        for part in reversed(key_parts):
            cur_dict = {part: cur_dict}
        out |= cur_dict
    return out


def _get_outpath_with_wildcards(out_path_root: str, param_names: Iterable[str]) -> str:
    """Get the output path with Snakemake wildcards in it.

    Parameter names are used for wildcards, with dots replaced with underscores.
    """
    outpath = Path(out_path_root)
    for name in param_names:
        outpath /= f"{name}_{{{name.replace('.','_')}}}"
    return str(outpath)


class VRExperiment:
    """Represents all parameter sets which are being tested."""

    MERGE_CONFIG_FILE = "vr_full_model_configuration.toml"
    OUTPUT_FILES = (
        MERGE_CONFIG_FILE,
        "initial_state.nc",
        "final_state.nc",
        "all_continuous_data.nc",
    )

    def __init__(self, out_path_root: str, param_grid: dict[str, Any]):
        """Create a new VRExperiment.

        param_grid is a nested dict containing the parameter values to be varied, which
        should be Iterables.

        Args:
            out_path_root: The folder used as a root by the different output folders
            param_grid: The grid of parameters to be used
        """
        params_flat: dict[str, Iterable] = _flatten_dict(param_grid)
        self._outpath = _get_outpath_with_wildcards(out_path_root, params_flat.keys())
        """The root output folder for all simulations."""
        self._param_set_dict = self._get_param_set_dict(params_flat)
        """The parameter sets to be used for each run, keyed by output path."""

    @property
    def all_outputs(self) -> list[str]:
        """Get all output files for the whole experiment."""
        return [
            str(dir / file)
            for dir, file in product(self._param_set_dict.keys(), self.OUTPUT_FILES)
        ]

    def _get_param_set_dict(
        self, params_flat: dict[str, Iterable]
    ) -> dict[Path, dict[str, Any]]:
        """Return a dict with parameter sets keyed by output path."""
        param_set_dict = {}
        for param_set in ParameterGrid(params_flat):
            args_dict = {
                key.replace(".", "_"): value for key, value in param_set.items()
            }

            outpath = self._outpath.format(**args_dict)
            param_set_dict[Path(outpath)] = _unflatten_dict(param_set)
        return param_set_dict

    @property
    def outpath(self) -> str:
        """The output folder to be used with wildcards for parameter values."""
        return self._outpath

    @property
    def output(self) -> list[str]:
        """Get outputs with wildcards for parameter values."""
        return [str(Path(self._outpath) / f) for f in self.OUTPUT_FILES]

    def run(self, input: Namedlist, output: Namedlist):
        """Run a simulation for the specified config to be saved in output."""
        outpath = Path(output[0]).parent
        if not all(Path(path).parent == outpath for path in output):
            raise RuntimeError("Output files are not all in same folder")

        params = self._param_set_dict[outpath]

        # Set outpath
        params |= {"core": {"data_output_options": {"out_path": str(outpath)}}}

        # Run simulation
        vr_run(input, params, outpath / self.MERGE_CONFIG_FILE)


if __name__ == "__main__":
    # Test _flatten_dict
    test_dict = {"a": {"b": "value"}}
    assert _flatten_dict(test_dict) == {"a.b": "value"}
    unflattened = _unflatten_dict({"a.b": "value"})
    assert unflattened == test_dict

    # Test VRSimulation
    params = {
        "hydrology": {"initial_soil_moisture": (0.1, 0.5, 0.9)},
        "another": {"param": (5,)},
    }
    sim = VRExperiment("out", params)
    print(f"OUTPATH: {sim._outpath}")
    print(list(sim.all_outputs))
