import cmor
import xcdat as xc
import xarray as xr
import cftime
import numpy as np
import sys, os, glob
from datetime import datetime

# USING CMOR WITH MODIFIED CORDEX SPECIFICATIONS FOR LOCA2 DATA @NERSC PERLMUTTER
# PJG  10092024 First test
# PJG  10142024 Generalized to all CMIP mods
# PJG  10302024 Modifying global atts
# PJG  11052024 added inputs to run via GNU parallel
# PJG  02052025 added if for LOCA2-1 version of 'pr'

# %% Get current script path, append src dir
current_dir = os.path.dirname(os.path.abspath(__file__))
new_path = os.path.join(current_dir, "..", "..", "src")
sys.path.append(new_path)
from DRCDPLib import writeUserJson


# multi = False
# if multi == True:
#    expi = sys.argv[1]
#    modi = sys.argv[3]
#    vari = sys.argv[2]
#    inputVarName = vari
#    outputVarName = vari
#    if vari == "pr":
#        outputUnits = "kg m-2 s-1"
#    if vari == "tasmax":
#        outputUnits = "K"
#    if vari == "tasmin":
#        outputUnits = "K"

# %% hard code vars and units
expi = "historical"
modi = "ACCESS-CM2"
vari = "tasmax"
inputVarName = vari
outputUnits = "K"


cmorTable = "../../Tables/DRCDP_CV.json"
inputJson = "LOCA2-0_CMIP6_input.json"

inputFilePath = (
    "/global/cfs/projectdirs/m3522/cmip6/LOCA2/*/0p0625deg/r1i1p1f1/historical/"
    + vari
    + "/*v2022*.nc"
)  # v20220519.nc'
inputFilePath = "/p/user_pub/PCMDIobs/obs4MIPs_input/DRCDP/tmp/*.nc"  # TEST ON GATES

if vari == "pr":  # LOCA2.1
    inputFilePath = (
        "/global/cfs/projectdirs/m3522/cmip6/LOCA2/*/0p0625deg/r1i1p1f1/historical/"
        + vari
        + "/*v20240915*.nc"
    )


def extract_date(ds):  # preprocessing function when opening multiple files
    for var in ds.variables:
        if var == "time":
            dataset_time = ds[var].values
            dataset_units = ds[var].units
            ds.assign(time=dataset_time)
            ds["time"].attrs = {"units": dataset_units}
    return ds


# EXPs, TRAP CMIP6 MODS AND RUNS
mod_runs = {}
exps = ["historical", "ssp245", "ssp585"]
exps = [expi]
for exp in exps:
    infile = inputFilePath.replace("historical", exp)
    lst = glob.glob(infile)
    mods = []
    for l in lst:
        mod = l.split(".")[1]
        if mod not in mods:
            mods.append(mod)
    mod_runs[exp] = {}
    for mod in mods:
        infile = infile.replace("/*/", "/" + mod + "/")
        infile = infile.replace("r1i1p1f1", "r*i1p1f1")
        infile = infile.replace("historical", exp)
        lst1 = glob.glob(infile)
        rn = []
        for l in lst1:
            rni = l.split(".")[3]
            if rni not in rn:
                rn.append(rni)
        rn.sort()
        mod_runs[exp][mod] = rn

yrs_hist = [
    ("1950", "1954"),
    ("1955", "1959"),
    ("1960", "1964"),
    ("1965", "1969"),
    ("1970", "1974"),
    ("1975", "1979"),
    ("1980", "1984"),
    ("1985", "1989"),
    ("1990", "1994"),
    ("1995", "1999"),
    ("2000", "2004"),
    ("2005", "2009"),
    ("2010", "2014"),
]
# yrs = [yrs[0]]     ###

yrs_scen = [
    ("2015", "2019"),
    ("2020", "2024"),
    ("2025", "2029"),
    ("2030", "2034"),
    ("2035", "2039"),
    ("2040", "2044"),
    ("2045", "2049"),
    ("2050", "2054"),
    ("2055", "2059"),
    ("2060", "2064"),
    ("2065", "2069"),
    ("2070", "2074"),
    ("2075", "2079"),
    ("2080", "2084"),
    ("2085", "2089"),
    ("2090", "2094"),
    ("2095", "2099"),
]

# mods = [mods[0]]   ###
# if multi == True:
#    exps = [expi]
# if multi == True:
#    mods = [modi]

exps = [expi]
mods = [modi]

print("exps and mods are: ", exps, mods)

for mod in mods:
    for exp in exps:
        rns = mod_runs[exp][mod]
        rns = [rns[0]]  ###
        for ri in rns:
            print("start1")
            infile = inputFilePath.replace("/*/", "/" + mod + "/")
            infile = infile.replace("/pr.*", "/pr." + mod + "*")
            infile = infile.replace("historical", exp)
            infile = infile.replace("r1i1p1f1", ri)
            if exp == "historical":
                yrs = yrs_hist
            if exp in ["ssp245", "ssp585"]:
                yrs = yrs_scen

            for yr in yrs:
                print("start2")
                start_time = datetime.now()
                fc = xc.open_mfdataset(
                    infile,
                    # decode_times=True,
                    # use_cftime=True,  # , preprocess=extract_date
                )
                f = fc
                # check time values
                print("check time values from infile")
                print(f.time.values)
                print("*****")
                f = fc.sel(time=slice(yr[0], yr[1]))
                print("check time values from dataset selection")
                print(f.time.values)
                sys.exit()
                d = f[inputVarName]

                lat = f.lat.values
                # print("lat", lat)
                lon = f.lon.values
                # print("lon", lon)
                time = f.time.values
                print("time", time)
                tunits = "days since 1900-01-01"

                print("start3 - adding bounds")
                f = f.bounds.add_bounds("X")
                f = f.bounds.add_bounds("Y")
                f = f.bounds.add_bounds("T")
                print("start4 - bounds added")

                ##### CMOR setup
                print("cmor start1")
                cmor.setup(
                    inpath="./",
                    netcdf_file_action=cmor.CMOR_REPLACE_4,
                    logfile=exp + "-" + mod + "-" + ri + "-" + "cmorLog.txt",
                )
                cmor.dataset_json(inputJson)
                cmor.dataset_json(writeUserJson(inputJson, cmorTable))
                cmor.load_table(cmorTable)

                # SET CMIP MODEL SPECIFIC ATTRIBUTES
                print("cmor start2")
                cmor.set_cur_dataset_attribute("source_id", "LOCA2--" + mod)
                cmor.set_cur_dataset_attribute("driving_source_id", mod)
                cmor.set_cur_dataset_attribute("driving_variant_label", ri)
                cmor.set_cur_dataset_attribute("driving_experiment_id", exp)

                # Create CMOR axes
                print("cmor start3")
                cmorLat = cmor.axis(
                    "latitude",
                    coord_vals=lat[:],
                    cell_bounds=f.lat_bnds.values,
                    units="degrees_north",
                )
                cmorLon = cmor.axis(
                    "longitude",
                    coord_vals=lon[:],
                    cell_bounds=f.lon_bnds.values,
                    units="degrees_east",
                )
                tbds = cftime.date2num(f.time_bnds.values[:], tunits).astype(np.float64)

                print("time")
                print(time)
                print(cftime.date2num(time, tunits).astype(np.float64))
                sys.exit()

                cmorTime = cmor.axis(
                    "time",
                    coord_vals=cftime.date2num(time, tunits).astype(np.float64),
                    cell_bounds=tbds,
                    units=tunits,
                )
                cmoraxes = [cmorTime, cmorLat, cmorLon]
                # Setup units and create variable to write using cmor - see https://cmor.llnl.gov/mydoc_cmor3_api/#cmor_set_variable_attribute
                varid = cmor.variable(
                    outputVarName, outputUnits, cmoraxes, missing_value=1.0e20
                )
                values = np.array(d[:], np.float32)

                # turn off erroneous variable attributes
                # cmor.set_variable_attribute(varid, "valid_min", "f", 2.0)
                # cmor.set_variable_attribute(varid, "valid_max", "f", 3.0)

                cmor.set_deflate(varid, 1, 1, 1)
                # shuffle=1,deflate=1,deflate_level=1 - Deflate options compress file data
                cmor.write(varid, values, len(time))
                # Write variable with time axis
                cmor.close()
                f.close()
                fc.close()
                end_time = datetime.now()
                print(
                    "done cmorizing ",
                    mod,
                    exp,
                    ri,
                    yr[0],
                    "-",
                    yr[1],
                    " process time: {}".format(end_time - start_time),
                )
