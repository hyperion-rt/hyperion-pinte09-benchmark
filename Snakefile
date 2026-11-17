configfile: "config.yaml"

PROFILE = config.get("profile", "full")

if PROFILE not in config["profiles"]:
    raise ValueError(
        "Unknown profile '{0}', should be one of: {1}".format(
            PROFILE, ", ".join(config["profiles"])
        )
    )

SETTINGS = config["profiles"][PROFILE]

# Results for the full profile go in e.g. sph_0.9.12, and results for any
# other profile go in e.g. sph_0.9.12_fast, so that reduced runs can never be
# mistaken for (or overwrite) the real benchmark results.
LABEL = str(config["version"])
if PROFILE != "full":
    LABEL += "_" + PROFILE

RUN = "{geometry}_" + LABEL
PLOTS = "plots_{geometry}_" + LABEL

GEOMETRIES = ["sph", "cyl"]
TAUS = ["1e+03", "1e+04", "1e+05", "1e+06"]
FORMATS = ["png", "eps"]


wildcard_constraints:
    geometry="sph|cyl",
    kind="models|models_images",
    tau=r"1e\+0[3-6]",


rule all:
    input:
        expand(
            PLOTS + "/{plot}.{ext}",
            geometry=GEOMETRIES,
            plot=["seds", "temperatures", "images_I", "images_linpol"],
            ext=FORMATS,
        ),


rule setup_model:
    input:
        dust="dust/pinte_dust.hdf5",
        wavelengths="benchmark/data/wavelength_points.txt",
    output:
        RUN + "/models/tau{tau}.rtin",
    params:
        settings=SETTINGS["models"],
    script:
        "scripts/setup_{wildcards.geometry}.py"


# The image models re-use the temperatures from the most optically thick model
rule setup_image:
    input:
        model=RUN + "/models/tau1e+06.rtout",
    output:
        RUN + "/models_images/tau1e+06.rtin",
    params:
        settings=SETTINGS["images"],
    script:
        "scripts/setup_image_{wildcards.geometry}.py"


rule run_hyperion:
    input:
        RUN + "/{kind}/tau{tau}.rtin",
    output:
        RUN + "/{kind}/tau{tau}.rtout",
    log:
        RUN + "/{kind}/tau{tau}.log",
    threads: config["mpi_processes"]
    resources:
        mpi_jobs=1,
    shell:
        "mpirun -n {threads} hyperion_{wildcards.geometry}_mpi {input} {output} > {log} 2>&1"


rule plot_seds:
    input:
        expand(RUN + "/models/tau{tau}.rtout", tau=TAUS, allow_missing=True),
    output:
        expand(PLOTS + "/seds.{ext}", ext=FORMATS, allow_missing=True),
    params:
        run=RUN,
        plots=PLOTS,
    shell:
        "python scripts/plot_seds.py {params.run} {params.plots}"


rule plot_temperatures:
    input:
        expand(RUN + "/models/tau{tau}.rtout", tau=["1e+03", "1e+06"], allow_missing=True),
    output:
        expand(PLOTS + "/temperatures.{ext}", ext=FORMATS, allow_missing=True),
    params:
        run=RUN,
        plots=PLOTS,
    shell:
        "python scripts/plot_temperatures.py {params.run} {params.plots}"


rule plot_images:
    input:
        RUN + "/models_images/tau1e+06.rtout",
    output:
        expand(
            PLOTS + "/images_{stokes}.{ext}",
            stokes=["I", "linpol"],
            ext=FORMATS,
            allow_missing=True,
        ),
    params:
        run=RUN,
        plots=PLOTS,
    shell:
        "python scripts/plot_images.py {params.run} {params.plots}"
