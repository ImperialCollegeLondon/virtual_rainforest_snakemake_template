from virtual_rainforest import example_data_path
from snakemake_helper import VRExperiment

# The parameter grid to be used for the simulation
PARAMS = {
    "hydrology": {"initial_soil_moisture": (0.5, 0.9)},
    "core": {"layers": {"soil_layers": range(2, 4)}},
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
