# CEE 586 project: from a soil column to a watershed

**Students: open [START_HERE.md](START_HERE.md) for the step-by-step plan.**  This README covers setup options and background.

Models and notebooks for the CEE 586 Physical Hydrology project.  You will follow water from the land surface into the subsurface and out of a watershed at three scales, all with ParFlow.

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/reedmaxwell/cee586_project)

| Folder | Part | What it holds |
|---|---|---|
| `part1_column/` | 1 | Single column ParFlow-CLM notebooks (snow and ET versions) and a runoff notebook |
| `part2_hillslope/` | 2 | The hillslope runoff-generation notebook, with movies of each run |
| `part3_east_river/` | 3 | The East River ParFlow-CLM model for Water Year 2017, with observations and scoring |
| `assignment/` | | The project assignment |
| `my_work/` | | A place for your own scripts, figures and write-up.  Git ignores everything in it. |

All three parts run on one ParFlow build, so you need to set up only once.

## Choose where to run

There are three ways to run the project.  They give the same results.

| Option | Who it suits | Cost |
|---|---|---|
| A. GitHub Codespaces | Anyone.  Nothing to install. | Uses your monthly Codespaces hours |
| B. Mac binary | Apple Silicon Macs (M1 or later) | Free, runs on your laptop |
| C. Docker | Windows, Intel Macs, Linux | Free, runs on your computer |

If you are short on Codespaces hours, use B or C.

### A. GitHub Codespaces

1. Sign in to GitHub and click the **Open in GitHub Codespaces** button above.
2. Leave the defaults (a 2-core machine) and click **Create codespace**.  It downloads a ready-made image, so it starts in a few minutes.
3. When VS Code opens in your browser, open a terminal and run `python check_environment.py`.

To save hours:

- Stop the codespace when you finish.  Go to [github.com/codespaces](https://github.com/codespaces), click **...** next to it and choose **Stop codespace**.  It stops by itself after 30 minutes idle, but those 30 minutes count.
- Come back to the same codespace.  Do not create a new one each time.
- Delete codespaces from earlier assignments that you no longer need.  Stopped codespaces still use your storage allowance.
- Verified students get more hours through [GitHub Education](https://github.com/education/students).

GitHub deletes a codespace that has not been used for 30 days.  Download anything you want to keep.

### B. Mac binary (Apple Silicon)

This is a ParFlow built for the class that runs with no compiler and no Docker.

```bash
# 1. Get this repository
git clone https://github.com/reedmaxwell/cee586_project.git
cd cee586_project

# 2. Download and unpack ParFlow (it unpacks to a folder named install)
curl -LO https://github.com/reedmaxwell/cee586_project/releases/download/parflow-east-river-2026/parflow-east-river-2026-macos-arm64.tar.gz
tar xzf parflow-east-river-2026-macos-arm64.tar.gz

# 3. Remove the macOS quarantine flag (the binaries are not notarized by Apple)
xattr -dr com.apple.quarantine install/

# 4. Tell your shell where ParFlow is
export PARFLOW_DIR=$PWD/install
export PATH=$PARFLOW_DIR/bin:$PATH

# 5. Make a Python environment and install the tools
python3 -m venv ~/cee586-env
source ~/cee586-env/bin/activate
pip install --prefer-binary -r requirements.txt
pip install $PARFLOW_DIR/python        # pftools that matches this ParFlow

# 6. Check, then start Jupyter
python check_environment.py
jupyter lab
```

Use Python 3.10 to 3.13.  Each time you open a new terminal, repeat the two `export` lines and the `source` line, or add them to your `~/.zshrc`.

Install `pftools` from the download as shown, not from PyPI.  The PyPI release does not match the class build.

### C. Docker (Windows, Intel Mac, Linux)

1. Install [Docker Desktop](https://docs.docker.com/get-docker/) and [VS Code](https://code.visualstudio.com/) with the **Dev Containers** extension.  On Windows, Docker Desktop uses WSL 2.
2. Clone this repository and open the folder in VS Code.
3. Choose **Reopen in Container** when VS Code offers it (or run **Dev Containers: Reopen in Container** from the command palette).  It downloads the same image Codespaces uses.
4. Open a terminal in VS Code and run `python check_environment.py`.

If you prefer plain Docker with Jupyter in your browser:

```bash
docker run --rm -it -p 8888:8888 -v "$PWD":/work -w /work ghcr.io/reedmaxwell/cee586_project:latest \
    jupyter lab --ip=0.0.0.0 --no-browser
```

On Windows PowerShell use `${PWD}` in place of `"$PWD"`.  Open the link that Jupyter prints.

## How to work

- Run the notebooks where they are.  They find their inputs by relative paths, so a copy in another folder will not run.  Keep your own scripts, figures and write-up in `my_work/`.
- To get updates posted after you started: `git pull` from the repository folder.
- Every run writes to its own folder (`runs/` or `overland_hillslope_runs/`).  These folders are not tracked by git.

## Part 1: single column

Work in `part1_column/snow/` or `part1_column/et/`.  Each has three notebooks, run in order:

1. `locate_plot_station_get_forcing.ipynb` chooses the site and downloads the forcing
2. `Single_Column_PFCLM_netcdf.ipynb` runs the column
3. `pfclm_snotel_compare.ipynb` or `pfclm_ameriflux_compare.ipynb` compares it with observations

The first notebook downloads forcing from HydroData, which needs a free account.  Register your PIN as the notebook describes.

`part1_column/4_pfclm_runoff_class.ipynb` computes runoff from a finished column run and reruns the column with new soil properties or a new water table depth.

## Part 2: hillslope

Open `part2_hillslope/runoff-generation.ipynb`.  It runs in a few seconds.  The notebook runs the baseline, plots it, plays a movie of it, and gives you a cell to change one value and run again under a new name.

## Part 3: East River

From a terminal:

```bash
cd part3_east_river
bash scripts/get_forcing.sh                                  # one time: downloads the forcing, about 720 MB
python scripts/run_east_river.py --hours 240 --name er_test   # ten-day test
python scripts/run_east_river.py                             # full water year in runs/er_wy2017, about 5 to 15 minutes
python scripts/evaluate.py runs/er_wy2017                    # scores against streamflow, SWE and ET
```

`part3_east_river/README.md` describes the model, the forcing and the options.

## Where this came from

- `part1_column/` is from [reedmaxwell/single_column_PFCLM](https://github.com/reedmaxwell/single_column_PFCLM).
- `part2_hillslope/` is the runoff-generation exercise from the ParFlow short course, in the version used in [hydroframe/ParFlow_CUAHSI_VU](https://github.com/hydroframe/ParFlow_CUAHSI_VU), with plotting and movie tools added.
- `part3_east_river/` is from [reedmaxwell/east_river_pfclm](https://github.com/reedmaxwell/east_river_pfclm).
- ParFlow is built from the `east-river-2026` branch of [reedmaxwell/parflow](https://github.com/reedmaxwell/parflow), pinned to one commit.
