# This file is a simple example of a Snakefile for invoking Virtual Rainforest. It will
# run multiple simulations using the specified parameter grid and put the results in a
# folder called "out". For more information, consult README.md.

from virtual_rainforest import example_data_path
from snakemake_helper import VRExperiment

# The parameter grid to be used for the simulation
PARAMS = {
    "hydrology": {"initial_soil_moisture": (0.5, 0.9)},
}
exp = VRExperiment("out", PARAMS)


rule all:
    input:
        exp.all_outputs,


rule vr:
    input:
        # NB: You should replace this with the path to your config(s)
        example_data_path,
    output:
        exp.output,
    run:
        exp.run(input, output)
