set -a

a=0.6474786
g=0.6296066
kappa=4752.16

H_0=10
r_0=100
beta=1.125
alpha=-2.625

r_star=2
r_min=0.1
r_max=400

R_max=500

M=3e-5

# Observer latitude:
# (let ((mu 0.95) (pi (* 4 (atan 1)))) (- 90 (* (/ 180 pi) (acos mu))))

# Inclination:
# (let ((mu 0.05) (pi (* 4 (atan 1)))) (* (/ 180 pi) (acos mu)))

. ./mu.sh
case $mu in
0.05)
  observer_altitude=2.866;;
0.15)
  observer_altitude=8.627;;
0.25)
  observer_altitude=14.478;;
0.35)
  observer_altitude=20.487;;
0.45)
  observer_altitude=26.744;;
0.55)
  observer_altitude=33.367;;
0.65)
  observer_altitude=40.542;;
0.75)
  observer_altitude=48.590;;
0.85)
  observer_altitude=58.212;;
0.95)
  observer_altitude=71.805;;
esac

delta_x=3.5857

dl_midpt=1e-3
forced_scatters=2
forced_interactions=2

chiral_symmetry=1
equatorial_symmetry=1
azimuthal_symmetry=3

cpu_time_limit=2000

./disk-christophe "$@"

