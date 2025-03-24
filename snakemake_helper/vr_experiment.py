"""Helper functionality for using Virtual Rainforest with Snakemake.

The main functionality for this module lies in the VRExperiment class, which represents
all the parameter sets which are being tested.
"""

from collections.abc import Iterable, Sequence
from itertools import product
from pathlib import Path
from typing import Any, ClassVar

from virtual_ecosystem.core.config import config_merge
from virtual_ecosystem.entry_points import ve_run


def _permute_parameter_grid(
    param_grid: dict[str, Iterable],
) -> Iterable[dict[str, Any]]:
    """Generate each combination of parameters for the given parameter grid.

    This function is a generator so the grid is computed lazily.

    Args:
        param_grid: A dict where the key is the name of a param and the value is an
            Iterable of possible values.

    Returns:
        All combinations of parameters in sequence

    Examples:
        >>> list(_permute_parameter_grid({'a': range(2), 'b': range(3)}))
        [{'a': 0, 'b': 0}, {'a': 0, 'b': 1}, {'a': 0, 'b': 2}, {'a': 1, 'b': 0}, {'a': 1, 'b': 1}, {'a': 1, 'b': 2}]
    """  # noqa: E501
    if not param_grid:
        return

    items = sorted(param_grid.items())
    keys, values = zip(*items)
    for v in product(*values):
        yield dict(zip(keys, v))


def _flatten_dict(d: dict[str, Any]) -> dict[str, Any]:
    """Flatten nested dicts into a single top-level dict.

    Subkeys are separated by dots.

    Args:
        d: Top-level nested dict

    Returns:
        The flattened dict

    Examples:
        >>> _flatten_dict({'a': {'b': 1}})
        {'a.b': 1}
    """
    out: dict[str, Any] = {}
    for key, value in d.items():
        _flatten_dict_inner(out, key, value)
    return out


def _flatten_dict_inner(out: dict[str, Any], key_prefix: str, value: Any) -> None:
    """Flatten nested dicts.

    Used internally by _flatten_dict.

    Args:
        out: The dict to store values in
        key_prefix: The prefix of the key name. If there are sub-dicts, the key will be
            the names concatenated with dots.
        value: The value to assign to the new dict entry
    """
    if isinstance(value, dict):
        for key2, value2 in value.items():
            _flatten_dict_inner(out, f"{key_prefix}.{key2}", value2)
    else:
        out[key_prefix] = value


def _unflatten_dict(d: dict[str, Any]) -> dict[str, Any]:
    """Perform the opposite operation to _flatten_dict.

    Args:
        d: A nested dict

    Returns:
        The unflattened (nested) dict

    Examples:
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

    Args:
        out_path_root: The root output folder
        param_names: The names of all parameters under investigation

    Returns:
        The output path with Snakemake wildcards
    """
    outpath = Path(out_path_root)
    for name in sorted(param_names):
        outpath /= f"{name}_{{{name.replace('.', '_')}}}"
    return str(outpath)


class VRExperiment:
    """Represents all parameter sets which are being tested."""

    MERGE_CONFIG_FILE = "vr_full_model_configuration.toml"
    LOG_FILE = "ve_run.log"
    OUTPUT_FILES: ClassVar = {
        MERGE_CONFIG_FILE,
        LOG_FILE,
        "initial_state.nc",
        "final_state.nc",
        "all_continuous_data.nc",
    }

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
        """Return a dict with parameter sets keyed by output path.

        Args:
            params_flat: A flat dict of parameters to investigate
        """
        param_set_dict = {}
        for param_set in _permute_parameter_grid(params_flat):
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

    def run(self, input: Sequence[str], output: Sequence[str]):
        """Run a simulation for the specified config to be saved in output.

        Args:
            input: Input paths
            output: Output paths
        """
        outpath = Path(output[0]).parent
        if not all(Path(path).parent == outpath for path in output):
            raise RuntimeError("Output files are not all in same folder")
        if not all(Path(path).name in self.OUTPUT_FILES for path in output):
            raise RuntimeError("Unknown file given as output")

        params = self._param_set_dict[outpath]

        # Set outpath
        outpath_opt = {"core": {"data_output_options": {"out_path": str(outpath)}}}
        params, conflicts = config_merge(params, outpath_opt)
        if conflicts:
            raise RuntimeError("Outpath config option was set twice")

        # Run simulation
        ve_run(cfg_paths=input, override_params=params, logfile=outpath / self.LOG_FILE)
