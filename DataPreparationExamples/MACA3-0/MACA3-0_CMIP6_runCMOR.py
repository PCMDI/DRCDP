import cmor
import xcdat as xc
import xarray as xr
import cftime
import numpy as np
import sys, os, glob
from datetime import datetime

# %% Get current script path, append src dir
current_dir = os.path.dirname(os.path.abspath(__file__))
new_path = os.path.join(current_dir, "..", "..", "src")
sys.path.append(new_path)
from DRCDPLib import writeUserJson

cmorTable = '../../Tables/DRCDP_APday.json'
inputJson = 'MACA3-0_CMIP6_input.json'

multi  = True
if multi == True:
 expi = sys.argv[1]
 modi = sys.argv[3]
 vr = sys.argv[2]

# TEST RUN
# python -i MACA3-0_CMIP6_runCMOR.py historical pr GFDL-ESM2G
#

inputFilePath = '/global/cfs/projectdirs/m3522/cmip6/MACA/GFDL-ESM2G/macav2metdata_pr_GFDL-ESM2G_r1i1p1_historical_1950_1954_CONUS_daily.nc'
inputFilePath = '/global/cfs/projectdirs/m3522/cmip6/MACA/GFDL-ESM2G/macav2metdata_pr_GFDL-ESM2G_r1i1p1_historical_*_CONUS_daily.nc'

if vr == 'pr':
 inputVarName = 'precipitation'
 outputVarName = 'pr'
 outputUnits = 'kg m-2 s-1'
 units_conv = 86400. 
if vr == 'tasmax':
   inputVarName = 'tasmax'
   outputVarName = 'tasmax'
   outputUnits = 'K'
   units_conv = 273.15
if vr == 'tasmin':
   inputVarName = 'tasmin'
   outputVarName = 'tasmin'
   outputUnits = 'K'
   units_conv = 273.15

inputFilePath = inputFilePath.replace('_pr_','_'+vr+'_') 
inputFilePath = inputFilePath.replace('GFDL-ESM2G',modi)

exps = ['historical','ssp245', 'ssp585']
mods = ['MPI-ESM1-2-HR', 'TaiESM1', 'CMCC-ESM2', 'ACCESS-ESM1-5', 'MRI-ESM2-0', 'FGOALS-g3', 'NorESM2-MM', 'CanESM5', 'MIROC6', 'ACCESS-CM2', 'NorESM2-LM', 'MPI-ESM1-2-LR', 'BCC-CSM2-MR', 'NESM3']

yrs_hist = [('1950','1954'),('1955','1959'),('1960','1964'),('1965','1969'),('1970','1974'),('1975','1979'),('1980','1984'),('1985','1989'),('1990','1994'),('1995','1999'),('2000','2004'),('2005','2009'),('2010','2014')]
yrs_scen = [('2015', '2019'), ('2020', '2024'), ('2025', '2029'), ('2030', '2034'), ('2035', '2039'), ('2040', '2044'), ('2045', '2049'), ('2050', '2054'), ('2055', '2059'), ('2060', '2064'), ('2065', '2069'), ('2070', '2074'), ('2075', '2079'), ('2080', '2084'), ('2085', '2089'), ('2090', '2094'), ('2095', '2099')]
yrs_all = yrs_hist + yrs_scen


if multi == True: exps = [expi]
if multi == True: mods = [modi]

print(modi, expi, vr, inputFilePath)

for mod in mods:
 for exp in exps:
    filelist = glob.glob(inputFilePath)

    fi = inputFilePath.replace('GFDL-ESM2G',modi)
    fc = xc.open_mfdataset(filelist,decode_times=True,use_cftime=True)
    fd = fc

    for yr in yrs_all:
     start_time = datetime.now()
     f = fd.sel(time=slice(yr[0]+ '-01-01',yr[1]+ '-01-01')) 
     d = f[inputVarName]
     lat = f.lat.values  
     lon = f.lon.values  
     time = f.time.values  
     tunits = "days since 1950-01-01"
     if vr in ['tasmin','tasmax']: d = np.add(d,units_conv)
     if vr in ['pr']: d = np.divide(d,units_conv)

     f = f.bounds.add_bounds("X") 
     f = f.bounds.add_bounds("Y")
     f = f.bounds.add_bounds("T")

# For more information see https://cmor.llnl.gov/mydoc_cmor3_api/
     cmor.setup(inpath='./',netcdf_file_action=cmor.CMOR_REPLACE_4,logfile=exp + '-' + mod + '-r1i1p1-'+ 'cmorLog.txt')
#    cmor.dataset_json(inputJson)
     cmor.dataset_json(writeUserJson(inputJson, cmorTable))
     cmor.load_table(cmorTable)

# SET CMIP MODEL SPECIFIC ATTRIBUTES 
#    cmor.set_cur_dataset_attribute("source_id","STAR-ESDM-v0--" + mod)
     cmor.set_cur_dataset_attribute("driving_source_id",mod)
     cmor.set_cur_dataset_attribute("driving_variant_label",'r1i1p1')
#    cmor.set_cur_dataset_attribute("driving_experiment_id",exp)
     cmor.set_cur_dataset_attribute("driving_experiment_id",'historical-' + exp)
#    cmor.set_cur_dataset_attribute("driving_grid_label",grid_label)

     if expi in ['historical']: cmor.set_cur_dataset_attribute("driving_activity_id",'CMIP') 
     if expi in ['ssp245','ssp585']: cmor.set_cur_dataset_attribute("driving_activity_id",'ScenarioMIP') 

     time_np = cftime.date2num(time,tunits)
     time_np = np.array(time_np[:],np.float32)  #time_np.astype(np.float32)  
     tbds_np = cell_bounds=cftime.date2num(f.time_bnds.values,tunits)
     tbds_np = np.array(tbds_np[:],np.float32)  #tbds_np.astype(np.float32)

# Create CMOR axes
     cmorLat = cmor.axis("latitude", coord_vals=lat[:], cell_bounds=f.lat_bnds.values, units="degrees_north")
     cmorLon = cmor.axis("longitude", coord_vals=lon[:], cell_bounds=f.lon_bnds.values, units="degrees_east")
     cmorTime = cmor.axis("time", coord_vals=time_np, cell_bounds=tbds_np, units= tunits)
     cmoraxes = [cmorTime,cmorLat, cmorLon]
# Setup units and create variable to write using cmor - see https://cmor.llnl.gov/mydoc_cmor3_api/#cmor_set_variable_attribute
     varid   = cmor.variable(outputVarName,outputUnits,cmoraxes,missing_value=1.e20)
     values  = np.array(d[:],np.float32)
     cmor.set_deflate(varid,0,0,0) ; # shuffle=1,deflate=1,deflate_level=1 - Deflate options compress file data
     cmor.write(varid,values,len(time)) ; # Write variable with time axis
     cmor.close()
     f.close()
     end_time = datetime.now()
     print('done cmorizing ',vr, mod, exp, 'r1i1p1', yr[0] + ' - ' + yr[1],' process time: {}'.format(end_time-start_time))
                                                          
