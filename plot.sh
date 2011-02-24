#!/bin/bash

rm plots_sph/*
rm plots_cyl/*

python scripts/plot_seds_paper.py cyl_0.7.1 plots_cyl
python scripts/plot_seds_paper.py sph_0.7.1 plots_sph

python scripts/plot_temperatures_paper.py cyl_0.7.1 plots_cyl
python scripts/plot_temperatures_paper.py sph_0.7.1 plots_sph

python scripts/plot_image_paper.py cyl_0.7.1 plots_cyl
python scripts/plot_image_paper.py sph_0.7.1 plots_sph
