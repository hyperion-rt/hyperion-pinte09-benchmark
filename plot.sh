#!/bin/bash

VERSION="0.8.4"

if [ ! -d "plots_cyl_$VERSION" ]; then
  mkdir "plots_cyl_$VERSION"
else
  rm plots_cyl_$VERSION/*
fi

if [ ! -d "plots_sph_$VERSION" ]; then
  mkdir "plots_sph_$VERSION"
else
  rm plots_sph_$VERSION/*
fi

python scripts/plot_seds.py "cyl_$VERSION" "plots_cyl_$VERSION"
python scripts/plot_seds.py "sph_$VERSION" "plots_sph_$VERSION"

python scripts/plot_temperatures.py "cyl_$VERSION" "plots_cyl_$VERSION"
python scripts/plot_temperatures.py "sph_$VERSION" "plots_sph_$VERSION"

python scripts/plot_images.py "cyl_$VERSION" "plots_cyl_$VERSION"
python scripts/plot_images.py "sph_$VERSION" "plots_sph_$VERSION"
