# This file is a simple example of a Snakefile for invoking Virtual Ecosystem. It will
# run multiple simulations using the specified parameter grid and put the results in a
# folder called "out". For more information, consult README.md.

from pathlib import Path
from virtual_ecosystem import example_data_path
from snakemake_helper import VEExperiment

# NB: You should replace this with the path to your config(s)
CONFIG_PATH = (Path(example_data_path) / "config",)

# The parameter grid to be used for the simulation
PARAMS = {
    "hydrology": {"initial_soil_moisture": (0.5, 0.9)},
}
exp = VEExperiment("out", PARAMS)


rule all:
    input:
        exp.all_outputs,


rule ve:
    input:
        CONFIG_PATH,
    output:
        exp.output,
    run:
        exp.run(input, output)
