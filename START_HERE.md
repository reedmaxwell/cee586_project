# Start here

This page is the game plan for the CEE 586 project.  Work through it from top to bottom.  The assignment itself is in `assignment/CEE586_project.md`.

These steps assume GitHub Codespaces.  To run on a Mac or with Docker instead, see the setup section of `README.md`.

---

## 0.  Set up (once, about 5 minutes)

- [ ] Open the repository on GitHub and choose **Code > Codespaces > Create codespace on main**.  Keep the 2-core machine.
- [ ] When VS Code opens in your browser, open a terminal (**Terminal > New Terminal**) and run:

  ```bash
  python check_environment.py
  ```

  The last line should say **All set.**
- [ ] When a notebook asks you to **Select Kernel**, choose **Python (PFCLM)**.
- [ ] Make a free HydroData account at https://hydrogen.princeton.edu/signup and get your PIN at https://hydrogen.princeton.edu/pin.  Part 1 needs it.

**Run notebooks where they are.**  The notebooks find their inputs by relative paths, so a copy in another folder will not run.  Your runs go into `runs/` folders that git ignores.

**Keep the browser tab open during long runs.**  A codespace stops after 30 minutes without activity in the tab, and a stopped codespace kills any run in progress.  Your files survive a stop.

---

## Part 1.  Single column (about 30 minutes of setup)

Work in `part1_column/snow/` for a SNOTEL site or `part1_column/et/` for the flux tower.  Run the three notebooks in order.

**Notebook 1:** `locate_plot_station_get_forcing.ipynb`

- [ ] In the **User Configuration** cell, set your site and `water_year = 2017`.
  - Snow: the notebooks are set up for `site_name = "Schofield_Pass"` and WY2017.  Butte needs an entry in `SNOTEL_SITES` in `part1_column/helpers.py` first.
  - ET: set `site_id`, `start = "2016-10-01"`, `end = "2017-10-01"` and the tower latitude and longitude by hand.
- [ ] Put your email and PIN in the `hf.register_api_pin(...)` line.  Do not commit this notebook with your PIN in it.
- [ ] Run all cells.  Note the run folder it prints, for example `../runs/snow/Schofield_Pass_WY2017`.

**Notebook 2:** `Single_Column_PFCLM_netcdf.ipynb`

- [ ] In the first code cell, check that `static_write_dir` is the run folder from Notebook 1.  It ships set to Schofield Pass WY2017 (snow) or the example AmeriFlux site (ET).
- [ ] Run all cells.  The soil and water table overrides (`soil_ksat`, `soil_porosity`, `wtd_m`) are at the top.  You change them for questions 2 to 4.

**Notebook 3:** `pfclm_snotel_compare.ipynb` or `pfclm_ameriflux_compare.ipynb`

- [ ] Set `static_write_dir` the same way, then run all cells.

**Notebook 4:** `part1_column/4_pfclm_runoff_class.ipynb`

- [ ] Set `static_write_dir` to your run folder, then run all cells.  It computes runoff and reruns the column with new soil or water table values.

Observations and forcing corrections for questions 1D and 1E are in `part3_east_river/inputs/`.

---

## Part 2.  Hillslope (seconds per run)

- [ ] Open `part2_hillslope/runoff-generation.ipynb` and run all cells.  The baseline run is named `dunne_over`.
- [ ] Use the modify-and-run cell for each new case.  Give each run a new name so you keep the old ones.

Runs go to `part2_hillslope/overland_hillslope_runs/`.

---

## Part 3.  East River (10 to 15 minutes per full year)

All commands run in a terminal from `part3_east_river/`.

```bash
cd part3_east_river
bash scripts/get_forcing.sh                                    # once: downloads 720 MB of forcing
python scripts/run_east_river.py --hours 240 --name er_test    # ten-day test
python scripts/run_east_river.py                               # full water year, into runs/er_wy2017
python scripts/evaluate.py runs/er_wy2017                      # scores against streamflow, SWE and ET
```

- [ ] Your scores and figure land in `results/`.  Compare them with the reference run in `results/reference/er_wy2017_scores.csv`.  They should match to the third decimal.

- [ ] `get_forcing.sh` must finish first.  If it has not, the run script stops with `Forcing not found`.
- [ ] For question 3.4, add `--name` to keep each experiment in its own folder, for example `--overland diffusive --name er_diffusive`.

`part3_east_river/README.md` describes the model, the forcing and every option.

---

## When you finish a session

- [ ] Download any figures you want to keep (right-click a file, then **Download**).
- [ ] Stop the codespace at https://github.com/codespaces (**...** > **Stop codespace**).  Come back to the same one next time.

## If something goes wrong

| What you see | What to do |
|---|---|
| `check_environment.py` says MISSING | Rebuild the codespace: **F1 > Codespaces: Rebuild Container** |
| A notebook cannot find `site_config.txt` | `static_write_dir` does not match the folder Notebook 1 wrote |
| `Forcing not found` | Run `bash scripts/get_forcing.sh` in `part3_east_river/` |
| The codespace stopped during a run | Restart it and rerun.  Finished runs are still on disk. |
| Updates were posted after you started | Run `git pull` in the terminal |
