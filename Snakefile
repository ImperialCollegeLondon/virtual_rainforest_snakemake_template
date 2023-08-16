from virtual_rainforest import example_data_path

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
        (
            'vr_run "{input}" '
            ' --outpath "out/moisture_{wildcards.moisture}"'
            ' --merge "{output[0]}" '
            + param("hydrology.initial_soil_moisture", "{wildcards.moisture}")
        )
