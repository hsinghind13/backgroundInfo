from math import prod
import numpy as np
from scipy.sparse.linalg import svds
import pandas as pd
import nbragg
import matplotlib.pyplot as plt
import komplot as kplt



def no_nan_divide(x, y):
    return np.where(y != 0, np.divide(x, np.where(y != 0, y, 1)), 0)


def plot_slice_region(ax, slice_tuple, color="red"):
    y0, y1 = slice_tuple[0].start, slice_tuple[0].stop
    x0, x1 = slice_tuple[1].start, slice_tuple[1].stop
    ax.plot([x0, x1, x1, x0, x0], [y0, y0, y1, y1, y0], color=color)


"""
Load open beam run.
"""
path = ".npz"
npz = np.load(path)
vol_open = npz["vol"]


""" 
Construct rank-1 approximation to background/calibration run. 
The "averaged" open beam volume computed by averaging the spectra at each pixel and then
finding the best scale factor for each pixel represents a heuristic approach to finding a rank-1 representation 
that is correct *iff* all the spectra a scalar multiple of each other. 
The SVD-based approach here always gives the best rank-1 approximation to the volume. 
"""

vol_open_mx = vol_open.reshape((vol_open.shape[0], -1))
u, s, vt = svds(vol_open_mx.astype(np.float32), k=1)
del vol_open_mx
u = u[..., np.newaxis]
vt = vt.reshape((1,) + vol_open.shape[1:])
vol_open_lr = u * s * vt
del vol_open  # minimize memory usage

path = ".npz"
npz = np.load(path)
vol_sample = npz["vol"]

"""
Display selected channel transmission together with sample region.
"""
idx = 297
#rgn_slice = np.s_[220:250, 120:380]
rgn_slice = np.s_[330:360, 105:430]
#rgn_slice = np.s_[200:220, 105:430]
trans = no_nan_divide(vol_sample[idx], vol_open_lr[idx])
imv = kplt.imview(trans, cmap="viridis", show_cbar=True, vmin_quantile=0.02)
plot_slice_region(imv.axes, rgn_slice)

"""
Select region in middle of pellet, cut after channel 800, and take spatial mean.
"""
rgn_sample = vol_sample[0:800, *rgn_slice].mean(axis=(1, 2))
rgn_open = vol_open_lr[0:800, *rgn_slice].mean(axis=(1, 2))
rgn_sample_sigma = vol_sample[0:800, *rgn_slice].std(axis=(1, 2))
rgn_open_sigma = vol_open_lr[0:800, *rgn_slice].std(axis=(1, 2))


"""
Compute ratio and plot it.
"""
N = prod([r.stop-r.start for r in rgn_slice])   
trans = no_nan_divide(rgn_sample, rgn_open)
A = rgn_sample
sigma_A = rgn_sample_sigma
B = rgn_open
sigma_B = rgn_open_sigma
sigma = np.abs(trans) * np.sqrt((sigma_A / A) ** 2 + (sigma_B / B) ** 2)
wl = (
    np.arange(trans.size) + 1
) * 0.004420134940585  # convert channel number to wavelength
p = kplt.plot(wl, trans, xlabel="wavelength", ylabel="transmission")
ax = p.axes.fill_between(wl, trans - sigma, trans + sigma, alpha=0.25)

"""
Do nbragg fit and print/plot results.
"""
openbm = pd.DataFrame(
    {
        "stack": np.arange(rgn_open.size) + 1,
        "counts": rgn_open,
        #"err": np.sqrt(rgn_open / N),
        "err": rgn_open_sigma,
    }
)
sample = pd.DataFrame(
    {
        "stack": np.arange(rgn_sample.size) + 1,
        "counts": rgn_sample,
        #"err": np.sqrt(rgn_sample / N),
        "err": rgn_sample_sigma,
    }
)
data = nbragg.Data.from_counts(sample, openbm, tstep=1e-5, L=8.95)
al = nbragg.CrossSection(al=".ncmat")
zrh = nbragg.CrossSection(zrh=".ncmat")
xs = 0.2 * al + 0.8 * zrh

model = nbragg.TransmissionModel(
    xs, vary_background=True, vary_response=True, vary_weights=True, vary_tof=True
)
model.params["thickness"].set(value=1.2, min=1.0, max=1.4)
#model.params["norm"].set(value=0.33, min=0.2, max=0.5)
model.params["norm"].set(value=0.33, min=0.01, max=0.9)
model.params["t0"].set(value=0.0, min=0.0, max=1e-7)
model.params["L0"].set(value=1.0, min=0.98, max=1.02)

result = model.fit(data, wlmin=0.02, wlmax=3.5)
result.plot()
plt.show(block=False)
print(result.fit_report_text())

result.plot_total_xs(split_phases=True)
plt.show(block=False)

# result.values["zrh"]

