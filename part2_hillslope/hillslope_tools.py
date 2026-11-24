"""Read, plot and animate the hillslope runoff-generation runs.

The notebook runs ParFlow and keeps each experiment in its own folder under
overland_hillslope_runs/.  These functions load one of those runs and show it:

    import hillslope_tools as ht
    r = ht.load_run("dunne_over")
    ht.plot_run(r)          # one saturation frame and the outlet hydrograph
    ht.movie(r)             # saturation, ponded depth and hydrograph through time
    ht.compare_runs(["dunne_over", "high_K", "shallow_wt"])

Flow is reported per unit width in m2/h and time in hours, the same units as the
overland flow homework.
"""
import os
from glob import glob
from types import SimpleNamespace

import numpy as np
import matplotlib.pyplot as plt

RUNS_DIR = "overland_hillslope_runs"

# values of the baseline problem, used when a key cannot be read from the run
DEFAULTS = dict(dx=5.0, dy=1.0, dz=0.05, dt=0.01, slope=0.05, mannings=1.0e-5, rain=0.02, t_rain=0.3)


def _settings(run_dir, run_name):
    """Problem values from the run's key database, with the baseline values as a fallback."""
    p = dict(DEFAULTS)
    try:
        from parflow import Run
        keys = Run.from_definition(os.path.join(run_dir, f"{run_name}.pfidb")).to_dict()
        def get(key, name, f=float):
            if key in keys and keys[key] is not None:
                p[name] = f(keys[key])
        get("ComputationalGrid.DX", "dx")
        get("ComputationalGrid.DY", "dy")
        get("ComputationalGrid.DZ", "dz")
        get("TimeStep.Value", "dt")
        get("TopoSlopesX.Geom.domain.Value", "slope")
        get("Mannings.Geom.domain.Value", "mannings")
        get("Patch.z_upper.BCPressure.rain.Value", "rain", lambda v: abs(float(v)))
        if "Cycle.rainrec.rain.Length" in keys and "TimingInfo.BaseUnit" in keys:
            p["t_rain"] = float(keys["Cycle.rainrec.rain.Length"]) * float(keys["TimingInfo.BaseUnit"])
    except Exception as err:          # keep going with the baseline values
        print(f"note: using baseline problem values ({type(err).__name__}: {err})")
    return p


def load_run(run_name, runs_dir=RUNS_DIR):
    """Load one run.  Returns an object with the output arrays and derived quantities."""
    import parflow as pf
    run_dir = os.path.join(os.getcwd(), runs_dir, run_name)

    def seq(var):
        files = sorted(glob(os.path.join(run_dir, f"{run_name}.out.{var}.*.pfb")))   # sorted: time order on every system
        if not files:
            raise FileNotFoundError(f"No {var} output found for run {run_name!r} in {run_dir}")
        return pf.read_pfb_sequence(files)

    r = SimpleNamespace(name=run_name, run_dir=run_dir, **_settings(run_dir, run_name))
    r.sat, r.press, r.overland_sum = seq("satur"), seq("press"), seq("overlandsum")
    r.nt, r.nz, _, r.nx = r.press.shape
    r.L = r.nx * r.dx

    # cells outside the solid file hold a very large negative number
    r.active = r.press[0] > -1.0e30                                       # [nz, ny, nx]
    # the top active cell in each column is the land surface
    r.top = np.array([np.max(np.where(r.active[:, 0, i])[0]) for i in range(r.nx)])
    r.x = (np.arange(r.nx) + 0.5) * r.dx
    r.zc = (np.arange(r.nz) + 0.5) * r.dz
    r.z_surf = (r.top + 1) * r.dz

    # time at each pressure output [h]; the overland sum is accumulated over each
    # output interval, so it lines up with the last n_os pressure outputs
    r.t_press = np.arange(r.nt) * r.dt
    r.t_sum = r.t_press[-r.overland_sum.shape[0]:]

    # ponded depth at the land surface [m], for every time and column
    r.h_surf = np.maximum(r.press[:, r.top, 0, np.arange(r.nx)], 0.0)
    # outflow per unit width [m2/h]: from ParFlow's overland sum at the outlet cell (x = 0) ...
    r.outflow = r.overland_sum[:, 0, 0, 0] / r.dt / r.dy
    # ... and from Manning's equation on the ponded depth there, as a check
    r.outflow_m = (np.sqrt(r.slope) / r.mannings) * r.h_surf[:, 0] ** (5.0 / 3.0)

    r.sat_m = np.ma.masked_where(~np.broadcast_to(r.active, r.sat.shape), r.sat)
    return r


def summary(r):
    """Print the peak flow and the mass balance of a run."""
    q_eq = r.rain * r.L
    print(f"run {r.name}: {r.nt} pressure outputs, top cell at the outlet k = {r.top[0]}")
    print(f"  peak outflow  {r.outflow.max():.3f} m2/h   (rL for an impervious plane = {q_eq:.3f} m2/h)")
    print(f"  total outflow {r.outflow.sum() * r.dt * r.dy:.4f} m3   total rain {r.rain * r.t_rain * r.L * r.dy:.4f} m3")


def water_table(r, k):
    """Top of the saturated zone connected to the base of each column at output k [m].

    Water ponded on dry soil does not count.  The line reaches the land surface
    only where the column is saturated all the way up."""
    wt = np.zeros(r.nx)
    for i in range(r.nx):
        col = r.press[k, : r.top[i] + 1, 0, i]
        neg = np.where(col < 0.0)[0]
        if len(neg) == 0:
            wt[i] = r.z_surf[i]
        else:
            j = max(neg.min() - 1, 0)
            wt[i] = min(r.zc[j] + max(col[j], 0.0), r.z_surf[i])
    return wt


def _cross_section(ax, r, k):
    im = ax.imshow(r.sat_m[k, :, 0, :], vmin=0.2, vmax=1.0, origin="lower", aspect="auto", cmap="Blues",
                   interpolation="none", extent=[0, r.L, 0, r.nz * r.dz])
    ax.plot(r.x, r.z_surf, color="k", lw=1.0, drawstyle="steps-mid")
    line, = ax.plot(r.x, water_table(r, k), color="tab:red", lw=1.2, label="water table")
    ax.set_ylabel("z [m]")
    ax.legend(loc="upper left")
    return im, line


def plot_run(r, icount=None, t_hw=None, q_hw=None):
    """One saturation frame and the outlet hydrograph.

    icount is the output number for the saturation frame (default: the end of the rain).
    t_hw, q_hw: your own hydrograph from the overland flow homework, in hours and m2/h."""
    summary(r)
    if icount is None:
        icount = int(np.argmin(np.abs(r.t_press - r.t_rain)))
    icount = min(icount, r.nt - 1)
    fig, ax = plt.subplots(2, figsize=(8, 7))
    im, _ = _cross_section(ax[0], r, icount)
    ax[0].set_title(f"{r.name}: saturation at t = {r.t_press[icount]:.2f} h")
    ax[0].set_xlabel("x [m]  (outlet at x = 0)")
    fig.colorbar(im, ax=ax[0], label="saturation [-]")

    ax[1].plot(r.t_sum, r.outflow, label="ParFlow overland sum")
    ax[1].plot(r.t_press, r.outflow_m, "--", label="Manning on outlet depth")
    ax[1].axhline(r.rain * r.L, color="gray", ls=":", label="rL, impervious plane")
    if t_hw is not None:
        ax[1].plot(t_hw, q_hw, "k-", lw=1.0, label="overland flow HW solution")
    ax[1].set_xlabel("time [h]")
    ax[1].set_ylabel("outflow [m$^2$/h]")
    ax[1].legend()
    fig.tight_layout()
    plt.show()


def movie(r, step=1, interval=100, save=None):
    """Play a run: saturation cross section, ponded depth along the hillslope, outlet hydrograph.

    step: use every step-th output (a larger step makes a shorter movie).
    save: a file name ending in .gif to write the movie to disk as well."""
    from matplotlib import animation
    hmax = max(r.h_surf.max() * 1000.0, 1.0)
    fig, ax = plt.subplots(3, figsize=(8, 9), gridspec_kw={"height_ratios": [1.3, 1, 1]})
    im, wt_line = _cross_section(ax[0], r, 0)
    fig.colorbar(im, ax=ax[0], label="saturation [-]")
    title = ax[0].set_title("")

    pond, = ax[1].plot(r.x, r.h_surf[0] * 1000.0, color="tab:blue", marker="o", ms=3)
    ax[1].set_xlim(0, r.L)
    ax[1].set_ylim(0, 1.1 * hmax)
    ax[1].set_xlabel("x [m]  (outlet at x = 0)")
    ax[1].set_ylabel("ponded depth [mm]")

    ax[2].plot(r.t_sum, r.outflow, color="tab:blue")
    ax[2].axhline(r.rain * r.L, color="gray", ls=":")
    ax[2].axvspan(0, r.t_rain, color="tab:blue", alpha=0.08)
    marker, = ax[2].plot([r.t_press[0]], [0.0], "o", color="tab:red")
    ax[2].set_xlabel("time [h]  (shaded: rain)")
    ax[2].set_ylabel("outflow [m$^2$/h]")
    fig.tight_layout()

    def update(k):
        im.set_data(r.sat_m[k, :, 0, :])
        wt_line.set_ydata(water_table(r, k))
        pond.set_ydata(r.h_surf[k] * 1000.0)
        marker.set_data([r.t_press[k]], [np.interp(r.t_press[k], r.t_sum, r.outflow)])
        title.set_text(f"{r.name}:  t = {r.t_press[k]:.2f} h")
        return im, wt_line, pond, marker, title

    anim = animation.FuncAnimation(fig, update, frames=range(0, r.nt, step), interval=interval, blit=False)
    if save:
        anim.save(save, writer=animation.PillowWriter(fps=max(1, int(1000 / interval))))
    html = anim.to_jshtml()
    plt.close(fig)
    try:
        from IPython.display import HTML
        return HTML(html)
    except ImportError:
        return html


def compare_runs(run_names, runs_dir=RUNS_DIR, t_hw=None, q_hw=None):
    """Overlay the outlet hydrographs of several runs."""
    if not run_names:
        raise ValueError("Add at least one run name to run_names.")
    fig, ax = plt.subplots(figsize=(9, 5))
    for name in run_names:
        r = load_run(name, runs_dir)
        ax.plot(r.t_sum, r.outflow, label=name)
    ax.axhline(r.rain * r.L, color="gray", ls=":", label="rL, impervious plane")
    if t_hw is not None:
        ax.plot(t_hw, q_hw, "k-", lw=1.0, label="overland flow HW solution")
    ax.set_title("Outlet hydrographs")
    ax.set_xlabel("time [h]")
    ax.set_ylabel("outflow [m$^2$/h]")
    ax.legend(title="Run")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    plt.show()
