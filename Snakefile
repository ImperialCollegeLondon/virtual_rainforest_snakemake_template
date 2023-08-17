from virtual_rainforest import example_data_path
from snakemake_helper import VRExperiment

PARAMS = {
    "hydrology": {"initial_soil_moisture": (0.5, 0.9)},
    "core": {"layers": {"soil_layers": range(2, 4)}},
}
sim = VRExperiment("out", PARAMS)


rule all:
    input:
        sim.all_outputs,


rule vr:
    input:
        example_data_path,
    output:
        sim.output,
    run:
        sim.run(input, output)
