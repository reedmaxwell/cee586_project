"""Check that ParFlow and the Python tools are ready.  Run:  python check_environment.py"""
import os, shutil, subprocess, sys

ok = True
def report(label, good, detail=""):
    global ok
    ok = ok and good
    print(f"[{'ok' if good else 'MISSING'}] {label} {detail}")

pfdir = os.environ.get("PARFLOW_DIR", "")
report("PARFLOW_DIR is set", bool(pfdir), pfdir)
exe = os.path.join(pfdir, "bin", "parflow") if pfdir else shutil.which("parflow")
if exe and os.path.exists(exe):
    out = subprocess.run([exe, "-v"], capture_output=True, text=True)
    report("parflow runs", out.returncode == 0, (out.stdout or out.stderr).strip().splitlines()[0] if (out.stdout or out.stderr) else "")
else:
    report("parflow executable found", False)

for mod in ("parflow", "numpy", "pandas", "xarray", "netCDF4", "matplotlib", "subsettools", "hf_hydrodata"):
    try:
        m = __import__(mod)
        report(f"import {mod}", True, getattr(m, "__version__", ""))
    except Exception as err:
        report(f"import {mod}", False, f"({type(err).__name__})")

try:
    from parflow.tools import hydrology
    report("pftools matches the class build (diffusive overland flow helper)",
           "diffus" in open(hydrology.__file__).read().lower())
except Exception:
    report("parflow.tools.hydrology", False)

print("\nAll set." if ok else "\nSomething is missing.  See the README, or ask in class.")
sys.exit(0 if ok else 1)
