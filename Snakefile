# Once there is example data in the upstream virtual_rainforest repo, we should use that
# instead. See: https://github.com/ImperialCollegeLondon/virtual_rainforest/issues/265
example_data_path = "dummy_data"


rule all:
    input:
        expand(
            "out/moisture_{moisture}/simulation_output.toml", moisture=(0.1, 0.5, 0.9)
        ),


rule vr:
    input:
        example_data_path,
    output:
        "out/moisture_{moisture}/simulation_output.toml",
        "out/moisture_{moisture}/initial_state.nc",
        "out/moisture_{moisture}/final_state.nc",
        "out/moisture_{moisture}/all_continuous_data.nc",
    shell:
        'vr_run "{input}" --merge "{output[0]}" '
        r"""--param "core.data_output_options.out_path_initial=\"{output[1]}\"" """
        r"""--param "core.data_output_options.out_path_final=\"{output[2]}\"" """
        r"""--param "core.data_output_options.out_folder_continuous=\"out/moisture_{wildcards.moisture}\"" """
        "--param hydrology.initial_soil_moisture={wildcards.moisture} "
