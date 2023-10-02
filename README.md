# Virtual Rainforest Snakemake template

![GitHub CI](https://github.com/ImperialCollegeLondon/virtual_rainforest_snakemake_template/actions/workflows/ci.yml/badge.svg)
[![codecov](https://codecov.io/gh/ImperialCollegeLondon/virtual_rainforest_snakemake_template/graph/badge.svg?token=BN2Y4SE4W0)](https://codecov.io/gh/ImperialCollegeLondon/virtual_rainforest_snakemake_template)

This is a template repository for running [Virtual Rainforest] analyses using
[Snakemake]. Snakemake is a workflow management system, which allows for running jobs in
parallel on a number of backends, including multiple cores on the same machine as well
as cluster systems.

The idea with this repository is that it can be used as a foundation for different
analyses. To start a new analysis, you should clone this repository (and submodules),
make any modifications you need to the configuration files and [Snakefile], then commit
these to git. This should allow others to easily reproduce your work.

## Getting started

If you are planning on performing your own analyses, it is recommended that you make
your own repository for this so that you can record your parameter settings. To do this,
click the green "Use this template" button at the top of this page.

Then you will need to clone either your own repository or, if you have not made your own
copy, this one, e.g.:

```sh
git clone --recursive https://github.com/ImperialCollegeLondon/virtual_rainforest_snakemake_template.git
```

Note the extra `--recursive` flag! If you forgot to check out the submodules, you can do
so later by running:

```sh
git submodule update --init
```

Then you can install dependencies via [Poetry]:

```sh
poetry install
```

To activate your newly created virtual environment, run:

```sh
poetry shell
```

## Working with the Snakefile

Snakemake uses Snakefiles to specify workflows. [Look at the Snakefile] in this
repository to see an example workflow.

The Snakefile in this repository is set up to run Virtual Rainforest with a few
different parameters. If you just want to check that things are working, feel free to
skip this section for now.

If you want to use a different parameter grid, you need to modify the `PARAMS` variable.
The parameters to vary are specified in a nested `dict`, with the sections named in the
same way as in Virtual Rainforest's TOML config files. Each non-`dict` element must be
an `Iterable`. If you want to use one particular value for all of the runs, you
therefore need to wrap it in a `list` (or just set the parameter in one of your config
files).

To add extra processing steps (e.g. to combine data files or produce figures), you need
to create extra rules. For example, if you wanted to perform some analysis on the
generated output files using a script called `analysis_program`, you could replace the
existing `rule all` with something like this:

```snakemake
rule analysis:
    input:
        exp.all_outputs,
    output:
        "analysis_output.toml",
    shell:
        "analysis_program {input}"
```

## Running Snakemake locally

To run the workflow on your local machine, use the `snakemake` command. You need to
specify the maximum number of CPUs Snakemake is allowed to use with the `--cores` flag.
For example:

```sh
snakemake --cores all
```

Once the command finishes, you should have the results of your analysis in a folder
called `out`.

## Running Snakemake on the Imperial HPC

This section assumes that you already have an account on the Imperial HPC and are
comfortable accessing it via `ssh`. If not, please [consult the Getting Started page].
You should also have loaded Python 3 (using Anaconda is probably the easiest way) and
installed Poetry. Repeat the steps above to install and activate your Poetry virtual
environment.

There are two ways in which you can use Snakemake to run your analyses on the cluster.
Either you can submit a job which just runs `snakemake --cores all`, as you did when
running Snakemake locally. In this case, you must remember to request multiple CPU cores
and enough memory via `qsub` otherwise the job will run very slowly. Alternatively, you
can get Snakemake to submit the different tasks (i.e. simulation runs) as separate jobs
and await the result. We will now look at this latter option.

Snakemake allows users to set specific configuration options for a given HPC cluster,
via [profiles]. A profile for the Imperial HPC system is provided in the the [`pbs-icl`]
folder.. To use it, you can pass the `--profile` flag to `snakemake`, like so:

```sh
snakemake --profile pbs-icl
```

Snakemake will now wait for your jobs to complete.

Note that this configuration uses default resource limits which are rather low (e.g. the
estimated runtime of the jobs is set to 15 minutes). For bigger jobs, you will probably
want to change these resource limits. The best way to do this with Snakemake is via a
[workflow profile]. An example workflow profile is given in the [`workflow-profile`]
folder. You should modify the `config.yaml` file to request the resources your jobs will
need. To use it, you need to additionally pass the `--workflow-profile` flag, like so:

```sh
snakemake --profile pbs-icl --workflow-profile workflow-profile
```

[consult the Getting Started Page]: https://wiki.imperial.ac.uk/display/HPC/Getting+started
[Look at the Snakefile]: ./Snakefile
[`pbs-icl`]: ./pbs-icl
[Poetry]: https://python-poetry.org/
[profiles]: https://snakemake.readthedocs.io/en/stable/executing/cli.html#profiles
[Snakefile]: ./Snakefile
[Snakemake]: https://snakemake.readthedocs.io/en/stable/
[Virtual Rainforest]: https://github.com/ImperialCollegeLondon/virtual_rainforest
[workflow profile]: https://snakemake.readthedocs.io/en/stable/executing/cli.html#profiles
[`workflow-profile`]: ./workflow-profile
