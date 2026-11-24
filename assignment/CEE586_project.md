# CEE 586 Project: from a soil column to a watershed

For the last homework we will apply what we have learned in the second half of class to follow water from the land surface into the subsurface and out of a watershed.  You will work at three scales: a single column, a hillslope and a full watershed.  The watershed is the East River above Almont, Colorado, simulated with ParFlow-CLM for Water Year 2017.

The project has four parts.  Part 1 is a single column, part 2 is a hillslope, and part 3 is the East River model, which runs in about five to ten minutes for the full water year.

Model and notebooks:

* Single column PF-CLM: the snow or ET notebooks in https://github.com/reedmaxwell/single_column_PFCLM and Notebook Four (`4_pfclm_runoff_class.ipynb`)
* Hillslope: `runoff-generation.ipynb` and `domain.pfsol`
* East River: https://github.com/reedmaxwell/east_river_pfclm

## Reading

Read these three papers before you start Part 2.  Refer to them where the questions ask for the theoretical basis of a result and in the synthesis in Part 4.

* Freeze and Harlan (1969) presented the blueprint for a physically based model of hydrologic response.  Many modeling platforms follow from this conceptual model.
* Dunne and Black (1970) measured runoff from saturated areas near the channel on a Vermont hillslope.  This is the field evidence for the saturation excess (so-called Dunne flow) mechanism you will produce in Parts 1 and 2.
* Loague et al. (2010) use an integrated model to ask whether a hillslope has to be either Horton or Dunne, and show cases that are neither or maybe both.

## Part 1.  Single column: infiltration and runoff (45 points)

In this part we will explore single column behavior.  It explores excess infiltration, excess saturation, and sensitivity between water table and ET.

1. Set up and establish the baseline behavior for your experiment.
    A. Choose a single location in the East River watershed for this column (latitude and longitude) and use Water Year 2017.  The Pumphouse flux tower and the Butte SNOTEL site are good choices because they have observations.  Use `locate_plot_station_get_forcing.ipynb` to do this.  With the snow notebooks, Schofield Pass is already in the site catalog and Butte needs an entry added to `SNOTEL_SITES` in `helpers.py`.  With the ET notebooks, enter the tower location by hand, because Pumphouse is not an AmeriFlux site.
    B. Simulate one year of the single column PF-CLM model.  Use `Single_Column_PFCLM_netcdf.ipynb` to do this.  The soil properties and the water table depth (`soil_ksat`, `soil_porosity`, `wtd_m`) are set in the override block at the top of this notebook.  You will change them in (2) to (4).
    C. Plot the baseline results.  Key variables will be saturation (or soil moisture), runoff, SWE and ET.  The comparison notebook (`pfclm_snotel_compare.ipynb` or `pfclm_ameriflux_compare.ipynb`) and Notebook Four will help you do this.
    D. Compare your baseline with observations.  The snow comparison notebook fetches the SNOTEL SWE for your site and reports scores.  The East River repository also has daily SWE at the Butte and Schofield Pass SNOTEL sites (`inputs/obs/obs_swe_daily.csv`) and daily ET and latent heat flux at the Pumphouse tower starting 15 April 2017 (`inputs/obs/flux_tower_pumphouse_daily.csv`).  Site locations are in `inputs/obs/sites.csv`.  Plot the model against the observations at your site and report the bias, RMSE, correlation, NSE and KGE.  The `metrics` function in `scripts/evaluate.py` computes these.
    E. Repeat the baseline with corrected forcing.  The column notebooks use the raw CW3E forcing.  In this watershed CW3E has too little precipitation and its nights in the valley are too warm.  The East River model corrects both (see the forcing section of the repository README).  Apply the same corrections at your site: multiply precipitation by 1.37 at Butte, 1.38 at Schofield Pass or 1.29 at Pumphouse, and lower the air temperature by 2.0 °C at Butte or 6.3 °C at Pumphouse in hours with no shortwave radiation (Schofield Pass has no temperature correction).  In the 1D forcing file shortwave is the first column, precipitation the third and air temperature the fourth.  For another location the correction grids are in `inputs/forcing_correction/` and the formulas are in `scripts/make_forcing.py`.  How do the scores in (D) change?  Use the corrected forcing for the experiments in (2) to (4).
2. Explore the sensitivity between runoff and saturated hydraulic conductivity (K).
    A. Note how much runoff is generated in your baseline simulation.
    B. Run alternate experiments with higher and lower K values and calculate / plot the change in runoff.
    C. Discuss the theoretical basis for these changes.  Does your experimental results match the theory?  How would you calculate this outside of a model?
3. Explore the sensitivity between runoff and column storage.
    A. Raise and lower the porosity of your single column and repeat the simulations.  How does this change runoff?
    B. Raise and lower the water table depth by changing the bottom boundary pressure condition.  How does this change the runoff?
    C. Discuss the theoretical basis for these changes.  Does your experimental results match the theory?
4. For the experiments in (3) above now plot changes in LH flux for your column.
    A. How does the porosity impact LH flux?
    B. How does the WTD impact LH flux?
    C. Discuss the theoretical basis for these changes.  Does your experimental results match the theory?

## Part 2.  Hillslope: runoff generation (30 points)

1. Simulate the overland flow HW hillslope with ParFlow using the notebook included (`runoff-generation.ipynb` and `domain.pfsol`).  First run the base case for Hortonian flow (i.e. just run the notebook) and quantitatively compare output to your finite difference and analytical solutions from the overland flow HW.
2. Then, increase the hydraulic conductivity (as indicated in the notebook) so that a change in runoff production occurs.  What value is needed to accomplish this and why?  Is there flow at the outlet and why?
3. Next, adjust the water table depth as shown in the notebook.  What does this do to the production of runoff for the system?
4. For the case in (3), plot the pressure at the land surface along the hillslope at three meaningful times.  Where on the hillslope does runoff start, and how does that differ from the Hortonian case?  Relate what you see to your single column results in Part 1.

## Part 3.  Watershed: the East River (70 points)

1. (15 points) Run the model and evaluate it.  Run the ten-day test first, then the full water year with the shipped configuration.  Run the evaluation script and report the scores for streamflow, SWE and ET.  Where does the model do well and where does it not?  Give a physical reason for one mismatch.
2. (25 points) Build the annual water balance for the watershed from the model output: precipitation, ET, streamflow at Almont and the change in storage.  Split the storage change into snow, surface water and subsurface.  Express everything as a depth over the watershed.  Does the balance close?  Compare the simulated streamflow term with the USGS observations.
3. (20 points) Groundwater and runoff generation.  Map the water table depth at peak snowmelt and at the end of the water year.  Map the cells with water ponded at the land surface on the same two dates.  Where is groundwater shallow, and where does runoff reach the land surface?  Which of the mechanisms from Parts 1 and 2 do you see in the watershed?  What sustains streamflow in late summer?
4. (10 points) Run one experiment and compare it with the baseline using the same scores and the same water balance.  Choose one:
    * Forcing.  Run with the uncorrected forcing.  Build it with `python scripts/make_forcing.py --level 0`, which pulls the raw CW3E forcing from HydroData, and pass the new directory to the run script with `--forcing`.  How do the snowpack, the streamflow and the water balance change?  What does this say about precipitation uncertainty in mountain watersheds?
    * Overland flow.  Run with the diffusive wave in place of the kinematic wave (`--overland diffusive`).  Do the scores change?  Use the Froude number and the kinematic wave number from the 2D overland flow and routing HW to explain what you find.

## Part 4.  Synthesis (30 points)

1. (20 points) Compare your single column from Part 1 with the watershed model cell at the same location.  Compare ET, SWE and soil moisture through the year.  Both are ParFlow-CLM, but the land cover, the snow and ET options and the forcing are not the same.  List what differs between them and say which differences matter most for your location.
2. (10 points) In one page or less, say what each of the three models (column, hillslope, watershed) can and cannot tell you about how a watershed generates streamflow.

Include a clear, concise write-up of your results and discussion as a single document.  Please also include your codes / supporting files as well.  DO NOT include extensive model output for every case, only graphs and tables of results as needed to completely address the requirements of the assignment.  That is, the write-up should stand alone; for someone to follow your work clearly they need only to read this document.

## References

Assigned reading:

Dunne, T., and Black, R. D. (1970).  An experimental investigation of runoff production in permeable soils.  Water Resources Research, 6(2), 478–490.

Freeze, R. A., and Harlan, R. L. (1969).  Blueprint for a physically-based, digitally-simulated hydrologic response model.  Journal of Hydrology, 9(3), 237–258.

Loague, K., Heppner, C. S., Ebel, B. A., and VanderKwaak, J. E. (2010).  The quixotic search for a comprehensive understanding of hydrologic response at the surface: Horton, Dunne, Dunton, and the role of concept-development simulation.  Hydrological Processes, 24(17), 2499–2505.

Background on the East River and on the model:

DeFrates, A., Jadallah, N., Stone, H., and Maxwell, R. M. (2026).  Modeled reconfiguration of root water uptake amplifies warming-induced subsurface storage depletion in a high elevation catchment.  Environmental Research Communications, 8, 111007.

Hubbard, S.S., Williams, K.H., Agarwal, D., Banfield, J., Beller, H., Bouskill, N., Brodie, E., Carroll, R., Dafflon, B., Dwivedi, D., Falco, N., Faybishenko, B., Maxwell, R.M., Peter Nico, P., Steefel, C., Steltzer, H., Tokunaga, T., Tran, P.A., Wainwright, H. and Varadharajan C. The East River, CO Watershed: A Mountainous Community Testbed for Improving Predictive Understanding of Multi-Scale Hydrological-Biogeochemical Dynamics. Vadose Zone Journal, 17(1):1-25, doi:10.2136/vzj2018.03.0061, 2018.

Kollet, S. J., and Maxwell, R. M. (2006).  Integrated surface–groundwater flow modeling: a free-surface overland flow boundary condition in a parallel groundwater flow model.  Advances in Water Resources, 29(7), 945–958.

Kollet, S. J., and Maxwell, R. M. (2008).  Capturing the influence of groundwater dynamics on land surface processes using an integrated, distributed watershed model.  Water Resources Research, 44, W02402.

Ryken, A. C., Gochis, D., and Maxwell, R. M. (2022).  Unravelling groundwater contributions to evapotranspiration and constraining water fluxes in a high-elevation catchment.  Hydrological Processes, 36(1), e14449.
