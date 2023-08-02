# Once there is example data in the upstream virtual_rainforest repo, we should use that
# instead. See: https://github.com/ImperialCollegeLondon/virtual_rainforest/issues/265
example_data_path = "dummy_data"

# Folders where simulations will be saved to
outdir = "out/moisture_{moisture}"


def param(name, value):
    return f'--param "{name}={value}" '


def strparam(name, value):
    # Note the double-escaping of quotes
    return param(name, f'\\"{value}\\"')


rule all:
    input:
        expand(f"{outdir}/simulation_output.toml", moisture=(0.1, 0.5, 0.9)),


rule vr:
    input:
        example_data_path,
    output:
        f"{outdir}/simulation_output.toml",
        f"{outdir}/initial_state.nc",
        f"{outdir}/final_state.nc",
        f"{outdir}/all_continuous_data.nc",
    shell:
        # This is presently rather ugly, but can be made simpler when there's an easy
        # way to specify an output folder for vr_run.
        # See: https://github.com/ImperialCollegeLondon/virtual_rainforest/issues/271
        (
            'vr_run "{input}" --merge "{output[0]}" '
            + strparam("core.data_output_options.out_path_initial", "{output[1]}")
            + strparam("core.data_output_options.out_path_final", "{output[2]}")
            + strparam(
                "core.data_output_options.out_folder_continuous",
                "out/moisture_{wildcards.moisture}",
            )
            + param("hydrology.initial_soil_moisture", "{wildcards.moisture}")
        )
