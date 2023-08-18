# Virtual Rainforest Snakemake template

<!-- markdownlint-disable MD026 -->
## :construction: NOTE: This repository is still a work in progress! :construction:
<!-- markdownlint-enable MD026 -->

This is a template repository for running [Virtual Rainforest] analyses using
[Snakemake]. Snakemake is a workflow management system, which allows for running jobs in
parallel on a number of backends, including multiple cores on the same machine as well
as cluster systems.

The idea with this repository is that it can be used as a foundation for different
analyses. To start a new analysis, you should clone this repository (and submodules),
make any modifications you need to the configuration files and [Snakefile], then commit
these to git. This should allow others to easily reproduce your work.

## Getting started

First you need to clone this repository and check out its submodules:

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

## Running Snakemake locally

Snakemake uses Snakefiles to specify workflows. [Look at the Snakefile] in this
repository to see an example workflow.

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
