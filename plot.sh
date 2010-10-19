#!/bin/bash

rm plots_sph/*
rm plots_cyl/*

python scripts/plot_seds_paper.py cyl_18oct10 plots_cyl
python scripts/plot_seds_paper.py sph_18oct10 plots_sph

python scripts/plot_temperatures_paper.py cyl_18oct10 plots_cyl
python scripts/plot_temperatures_paper.py sph_18oct10 plots_sph

# python scripts/plot_image_paper.py cyl_13jul10 plots_cyl
# python scripts/plot_image_paper.py sph_13jul10 plots_sph
# 
# 
