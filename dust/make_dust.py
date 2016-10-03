from hyperion.dust import MieXDust

import numpy as np
np.seterr(all='ignore')

d = MieXDust('pinte_dust/pinte1mu')
d.optical_properties.extrapolate_wav(9.e-4, 1.e7)
d.plot('pinte_dust.png')
d.write('pinte_dust.hdf5')

