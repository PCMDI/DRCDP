#!/usr/bin/env python
# coding: utf-8

# # Pull CV entries files; strip out extraneous entries
# <div style="text-align: right">
# <p>
#     <img src="https://pcmdi.github.io/assets/PCMDI/199x65px-PCMDI-Logo-Text-rectangle.png"
#          width="91"
#          height="30"
#          class="fixed-height-image"
#          style="margin-right: 20px"
#          title="Program for Climate Model Diagnosis and Intercomparison"
#          alt="Program for Climate Model Diagnosis and Intercomparison"
#     >&nbsp;
#     <img src="https://pcmdi.github.io/assets/LLNL/212px-LLNLiconPMS286-WHITEBACKGROUND.png"
#          width="30"
#          height="30"
#          class="fixed-height-image"
#          style="margin-right: 20px"
#          title="Lawrence Livermore National Laboratory"
#          alt="Lawrence Livermore National Laboratory"
#     >&nbsp;
#     <img src="https://pcmdi.github.io/assets/DOE/459x127px-DOE-Logo_Color_TextOnly.png"
#          width="108"
#          height="30"
#          class="fixed-height-image"
#          style="margin-right: 20px"
#          title="United States Department of Energy"
#          alt="United States Department of Energy"
#     >
# </p>
# </div>

# **Summary:**
# 
# This file pulls a CMIP6Plus_CVs/CMOR3.9.0-era CV files, strips out
# extraneous entries and saves the files for local use
# 
# **Authors:**
# 
# Paul J. Durack ([durack1](https://github.com/durack1); [PCMDI](https://pcmdi.llnl.gov/), [Lawrence Livermore National Laboratory](https://www.llnl.gov/))
# 
# **Notes:**
# 
# PJD 15 Feb 2025 - initiated<br>
# PJD 15 Feb 2025 - first prototype functioning<br>
# PJD 16 Feb 2025 - add source_id contact and other info; Add DRS<br>
# PJD 16 Feb 2025 - reconstructed DRS and filename templates to order relevant information<br>
# PJD 18 Feb 2025 - updated to remove variant_info and variant_label from required_global_attributes<br>
# PJD 18 Feb 2025 - updated to remove variant_label from DRS<br>
# PJD 20 Feb 2025 - updated tracking_id -> tracking_id_prefix<br>
# PJD 20 Feb 2025 - update MACA3-0 registration, augment with available variables<br>
# PJD 24 Feb 2025 - updated source_version_number -> source_version<br>
# PJD 27 Feb 2025 - update license info<br>
# PJD  4 Mar 2025 - adding `gr` and `gr1` grid_labels ([#40](https://github.com/PCMDI/DRCDP/issues/40))<br>
# PJD 28 May 2025 - updating `license_id` and `region` CVs to match CMOR 3.10+ changes ([PCMDI/DRCDP/issues#40](https://github.com/PCMDI/DRCDP/issues/43))<br>
# PJD 28 May 2025 - updating `license["license_template"]` to match CMOR 3.10+ changes ([PCMDI/DRCDP/issues#40](https://github.com/PCMDI/DRCDP/issues/43))<br>
# PJD 24 Jun 2025 - update `DRCDP_CV.json:institution_id` following [PCMDI/DRCDP/issues#55](https://github.com/PCMDI/DRCDP/issues/55) and [WCRP-CMIP/WCRP-universe/issues#63](https://github.com/WCRP-CMIP/WCRP-universe/issues/63#issuecomment-3085735081)<br>
# PJD  2 Sep 2025 - update fix conflict><br>
# PJD  2 Sep 2025 - add EPA/EDDE2-0 registration information back in ([PCMDI/DRCDP/issues#50](https://github.com/PCMDI/DRCDP/issues/50))<br>
# PJD  2 Sep 2025 - add AP1hr table ([PCMDI/DRCDP/issues#50](https://github.com/PCMDI/DRCDP/issues/50))<br>
# PJD  2 Sep 2025 - augment `activity_id` to list/array type ([PCMDI/DRCDP/pull#57](https://github.com/PCMDI/DRCDP/pull/57/files))<br>
# 
# ***TODO:***
# 
# **Links:**

# ### imports

# In[1]:


get_ipython().run_cell_magic('time', '', 'import datetime\nimport json\nimport os\nimport requests\n')


# ### set table, coordinate, formula_terms and grids URLs and pull files

# In[2]:


get_ipython().run_cell_magic('time', '', 'urls = {\n    "frequency": "https://raw.githubusercontent.com/PCMDI/mip-cmor-tables/refs/heads/main/MIP_frequency.json",\n    "grid_label": "https://raw.githubusercontent.com/PCMDI/mip-cmor-tables/refs/heads/main/MIP_grid_label.json",\n    "license": "https://raw.githubusercontent.com/PCMDI/mip-cmor-tables/refs/heads/main/MIP_license.json",\n    "nominal_resolution": "https://raw.githubusercontent.com/PCMDI/mip-cmor-tables/refs/heads/main/MIP_nominal_resolution.json",\n    "realm": "https://raw.githubusercontent.com/PCMDI/mip-cmor-tables/refs/heads/main/MIP_realm.json",\n    "source_type": "https://raw.githubusercontent.com/PCMDI/obs4MIPs-cmor-tables/refs/heads/master/obs4MIPs_source_type.json",\n}\n# create: institution_id, product, required_global_attributes, source_id, table_id, tracking_id\n\n# loop through urls\nkeys = urls.keys()\nfor count, key in enumerate(keys):\n    print(count, key)\n    url = urls[key]\n    try:\n        response = requests.get(url)\n        response.raise_for_status()  # Raise HTTPError for bad responses (4/5xx)\n        vars()[key] = json.loads(response.text)\n    except requests.exceptions.RequestException as e:\n        print(f"Request failed: {e}")\n    except json.JSONDecodeError as e:\n        print(f"JSON decode failed: {e}")\n    except Exception as e:\n        print(f"Unexpected error occurred: {e}")\n')


# ### create DRS

# In[3]:


DRS = {}
DRS["DRS"] = {}
DRS["DRS"]["directory_path_template"] = "".join(
    [
        "<activity_id><region_id><institution_id><source_id><driving_mip_era>",
        "<driving_activity_id><driving_experiment_id><driving_source_id>",
        "<driving_variant_label><frequency><variable_id><version>",
    ]
)
DRS["DRS"][
    "directory_path_example"
] = "DRCDP/NAM/UCSD-SIO/LOCA2-1/CMIP6/CMIP/historical/ACCESS-CM2/r1i1p1f1/day/tasmax/v20250216"
DRS["DRS"]["filename_template"] = "".join(
    [
        "<variable_id><region_id><institution_id><source_id>",
        "<driving_mip_era><driving_experiment_id><driving_source_id>",
        "<driving_variant_label><frequency>",
    ]
)
DRS["DRS"][
    "filename_example"
] = "tasmax_NAM_UCSD-SIO_LOCA2-1_CMIP6_historical_ACCESS-CM2_r1i1p1f1_day_19500102-19500131.nc"
DRS


# ### process frequency

# In[4]:


frequency.pop("version_metadata")
keyList = list(frequency["frequency"].keys())
keepKey = ["1hr", "day"]
for count, key in enumerate(keyList):
    if key not in keepKey:
        frequency["frequency"].pop(key)
frequency


# ### process grid_label

# In[5]:


grid_label.pop("version_metadata")
keyList = list(grid_label["grid_label"].keys())
keepKey = ["gn", "gr", "gr1"]
for count, key in enumerate(keyList):
    if key not in keepKey:
        grid_label["grid_label"].pop(key)
grid_label["grid_label"]["gn"] = grid_label["grid_label"]["gn"].replace(
    "a model's ", "the analysis-"
)
grid_label


# ### create institution_id

# In[6]:


institution_id = {}
institution_id["institution_id"] = {}
institution_id["institution_id"]["EPA"] = {}
institution_id["institution_id"]["EPA"][
    "contact"
] = "Megan Mallard; Mallard.Megan@epa.gov"
institution_id["institution_id"]["EPA"][
    "name"
] = "United States Environmental Protection Agency, National Exposure Research Laboratory (NERL), Systems Exposure Division, 109 T.W. Alexander Drive, Durham, NC 27709, USA"
institution_id["institution_id"]["EPA"]["ROR"] = "03tns0030"
institution_id["institution_id"]["EPA"]["URL"] = "https://www.epa.gov/"
institution_id["institution_id"]["UCM-ACSL"] = {}
institution_id["institution_id"]["UCM-ACSL"][
    "contact"
] = "John T. Abatzoglou; jabatzoglou@ucmerced.edu"
institution_id["institution_id"]["UCM-ACSL"][
    "name"
] = "Applied Climate Science Laboratory, University of California, Merced, 5200 N. Lake Road, Merced, CA 95343, USA"
institution_id["institution_id"]["UCM-ACSL"]["ROR"] = "00d9ah105"
institution_id["institution_id"]["UCM-ACSL"]["URL"] = "https://www.climatologylab.org"
institution_id["institution_id"]["UCSD-SIO"] = {}
institution_id["institution_id"]["UCSD-SIO"][
    "contact"
] = "Daniel Feldman; DRFeldman@lbl.gov"
institution_id["institution_id"]["UCSD-SIO"][
    "name"
] = "Scripps Institution of Oceanography, University of California, San Diego, 9500 Gilman Drive, La Jolla, CA 92093, USA"
institution_id["institution_id"]["UCSD-SIO"]["ROR"] = "04v7hvq31"
institution_id["institution_id"]["UCSD-SIO"]["URL"] = "https://scripps.ucsd.edu"
institution_id["institution_id"]["TTU"] = {}
institution_id["institution_id"]["TTU"][
    "contact"
] = "Katharine Hayhoe; katharine.hayhoe@ttu.edu"
institution_id["institution_id"]["TTU"][
    "name"
] = "Texas Tech University, 2520 Broadway Avenue, Lubbock, TX 79409, USA"
institution_id["institution_id"]["TTU"]["ROR"] = "0405mnx93"
institution_id["institution_id"]["TTU"]["URL"] = "https://www.ttu.edu/"
institution_id


# ### process license

# In[7]:


# cleanup upstream metadata
license.pop("version_metadata")
license["license"].pop("license")
# remap license_template
license["license"]["license_template"] = " ".join(
    [
        "<license_id>; DRDCP data produced by <institution_id>",
        "is licensed under a <license_type> License (<license_url>).",
        "Consult https://pcmdi.llnl.gov/CMIP6/TermsOfUse",
        "for terms of use governing DRDCP output, including",
        "citation requirements and proper acknowledgment.",
        "The data producers and data providers make no",
        "warranty, either express or implied, including,",
        "but not limited to, warranties of merchantability",
        "and fitness for a particular purpose. All",
        "liabilities arising from the supply of the",
        "information (including any liability arising",
        "in negligence) are excluded to the fullest",
        "extent permitted by law.",
    ]
)

# remap license_options to license_id
license["license"]["license_id"] = {}
# CC BY 4.0
license["license"]["license_id"]["CC BY 4.0"] = {}
license["license"]["license_id"]["CC BY 4.0"]["license_type"] = license["license"][
    "license_options"
]["CC BY 4.0"]["license_id"]
license["license"]["license_id"]["CC BY 4.0"]["license_url"] = license["license"][
    "license_options"
]["CC BY 4.0"]["license_url"]
# CC0 1.0
license["license"]["license_id"]["CC0 1.0"] = {}
license["license"]["license_id"]["CC0 1.0"]["license_type"] = license["license"][
    "license_options"
]["CC0 1.0"]["license_id"]
license["license"]["license_id"]["CC0 1.0"]["license_url"] = license["license"][
    "license_options"
]["CC0 1.0"]["license_url"]
# cleanup
license["license"].pop("license_options")
# print license
license


# ### process nominal_resolution

# In[8]:


nominal_resolution.pop("version_metadata")
nominal_resolution


# ### create product

# In[9]:


product = {}
product["product"] = {}
product["product"] = ["downscaled-dynamical", "downscaled-statistical"]
product


# ### process realm

# In[10]:


realm.pop("version_metadata")
keyList = list(realm["realm"].keys())
keepKeys = ["atmos", "land"]
for count, key in enumerate(keyList):
    if key not in keepKeys:
        realm["realm"].pop(key)
realm


# ### create region

# In[11]:


region = {}
region["region"] = [
    "north_america",
]
region


# ### create required_global_attributes

# In[12]:


required_global_attributes = {}
required_global_attributes["required_global_attributes"] = [
    "Conventions",
    "activity_id",
    "calendar",
    "contact",
    "creation_date",
    "data_specs_version",
    "driving_activity_id",
    "driving_experiment_id",
    "driving_mip_era",
    "driving_source_id",
    "driving_variant_label",
    "frequency",
    "grid",
    "grid_label",
    "license",
    "license_id",
    "license_url",
    "nominal_resolution",
    "product",
    "realm",
    "region",
    "region_id",
    "table_id",
    "tracking_id",
    "variable_id",
]
required_global_attributes


# ### create source_id

# In[13]:


source_id = {}
source_id["source_id"] = {}
# EDDE2-0
source_id["source_id"]["EDDE2-0"] = {}
source_id["source_id"]["EDDE2-0"]["calendar"] = "gregorian"
source_id["source_id"]["EDDE2-0"]["contact"] = "Megan Mallard; Mallard.Megan@epa.gov"
source_id["source_id"]["EDDE2-0"]["further_info_url"] = ""
source_id["source_id"]["EDDE2-0"]["grid"] = "10 x 10 km latitude x longitude"
source_id["source_id"]["EDDE2-0"]["grid_label"] = "gn"
source_id["source_id"]["EDDE2-0"]["institution_id"] = "EPA"
source_id["source_id"]["EDDE2-0"][
    "license"
] = "Creative Commons Attribution 4.0 International"
source_id["source_id"]["EDDE2-0"]["license_id"] = "CC BY 4.0"
source_id["source_id"]["EDDE2-0"][
    "license_url"
] = "https://creativecommons.org/licenses/by/4.0/"
source_id["source_id"]["EDDE2-0"]["nominal_resolution"] = "10 km"
source_id["source_id"]["EDDE2-0"]["product"] = "downscaled-statistical"
source_id["source_id"]["EDDE2-0"]["reference"] = " ".join(
    [
        "Nolte, Christopher G., Tanya L. Spero, Jared H. Bowden,",
        "Marcus C. Sarofim, Jeremy Martinich, Megan S. Mallard",
        "(2021) Regional temperature-ozone relationships across",
        "the U.S. under multiple climate and emissions scenarios.",
        "Journal of the Air & Waste Management Association 74 (10),",
        "pp 1251-1264. https://doi.org/10.1080/10962247.2021.1970048",
    ]
)
source_id["source_id"]["EDDE2-0"]["region"] = "north_america"
source_id["source_id"]["EDDE2-0"]["region_id"] = "NAM"
source_id["source_id"]["EDDE2-0"][
    "source"
] = "EDDE 2.0: EPA Dynamically Downscaled Ensemble based on CMIP5"
source_id["source_id"]["EDDE2-0"]["source_name"] = "EDDE"
source_id["source_id"]["EDDE2-0"]["source_version"] = "2.0"
source_id["source_id"]["EDDE2-0"]["title"] = "EDDE 2.0 dataset prepared for DRCDP"
# LOCA2-0
source_id["source_id"]["LOCA2-0"] = {}
source_id["source_id"]["LOCA2-0"]["calendar"] = "gregorian"
source_id["source_id"]["LOCA2-0"]["contact"] = "Daniel Feldman; DRFeldman@lbl.gov"
source_id["source_id"]["LOCA2-0"]["further_info_url"] = "https://loca.ucsd.edu/"
source_id["source_id"]["LOCA2-0"]["grid"] = "5 x 5 km latitude x longitude"
source_id["source_id"]["LOCA2-0"]["grid_label"] = "gn"
source_id["source_id"]["LOCA2-0"]["institution_id"] = "UCSD-SIO"
source_id["source_id"]["LOCA2-0"][
    "license"
] = "Creative Commons Attribution 4.0 International"
source_id["source_id"]["LOCA2-0"]["license_id"] = "CC BY 4.0"
source_id["source_id"]["LOCA2-0"][
    "license_url"
] = "https://creativecommons.org/licenses/by/4.0/"
source_id["source_id"]["LOCA2-0"]["nominal_resolution"] = "5 km"
source_id["source_id"]["LOCA2-0"]["product"] = "downscaled-statistical"
source_id["source_id"]["LOCA2-0"]["reference"] = " ".join(
    [
        "Pierce, David W., Daniel R. Cayan, and Bridget L. Thrasher",
        "(2014) Statistical downscaling using Localized Constructed",
        "Analogs (LOCA). Journal of Hydrometeorology, 15 (6), pp",
        "2558-2585. https://doi.org/10.1175/JHM-D-14-0082.1",
    ]
)
source_id["source_id"]["LOCA2-0"]["region"] = "north_america"
source_id["source_id"]["LOCA2-0"]["region_id"] = "NAM"
source_id["source_id"]["LOCA2-0"][
    "source"
] = "LOCA 2.0: Statistically-downscaled climate model projections based on CMIP6"
source_id["source_id"]["LOCA2-0"]["source_name"] = "LOCA"
source_id["source_id"]["LOCA2-0"]["source_version"] = "2.0"
source_id["source_id"]["LOCA2-0"]["title"] = "LOCA 2.0 dataset prepared for DRCDP"
# LOCA2-1
source_id["source_id"]["LOCA2-1"] = {}
source_id["source_id"]["LOCA2-1"]["calendar"] = "gregorian"
source_id["source_id"]["LOCA2-1"]["contact"] = "Daniel Feldman; DRFeldman@lbl.gov"
source_id["source_id"]["LOCA2-1"]["further_info_url"] = "https://loca.ucsd.edu/"
source_id["source_id"]["LOCA2-1"]["grid"] = "5 x 5 km latitude x longitude"
source_id["source_id"]["LOCA2-1"]["grid_label"] = "gn"
source_id["source_id"]["LOCA2-1"]["institution_id"] = "UCSD-SIO"
source_id["source_id"]["LOCA2-1"][
    "license"
] = "Creative Commons Attribution 4.0 International"
source_id["source_id"]["LOCA2-1"]["license_id"] = "CC BY 4.0"
source_id["source_id"]["LOCA2-1"][
    "license_url"
] = "https://creativecommons.org/licenses/by/4.0/"
source_id["source_id"]["LOCA2-1"]["nominal_resolution"] = "5 km"
source_id["source_id"]["LOCA2-1"]["product"] = "downscaled-statistical"
source_id["source_id"]["LOCA2-1"]["reference"] = " ".join(
    [
        "Pierce, David W., Daniel R. Cayan, and Bridget L. Thrasher",
        "(2014) Statistical downscaling using Localized Constructed",
        "Analogs (LOCA). Journal of Hydrometeorology, 15 (6), pp",
        "2558-2585. https://doi.org/10.1175/JHM-D-14-0082.1",
    ]
)
source_id["source_id"]["LOCA2-1"]["region"] = "north_america"
source_id["source_id"]["LOCA2-1"]["region_id"] = "NAM"
source_id["source_id"]["LOCA2-1"][
    "source"
] = "LOCA 2.1: Statistically-downscaled climate model projections based on CMIP6"
source_id["source_id"]["LOCA2-1"]["source_name"] = "LOCA"
source_id["source_id"]["LOCA2-1"]["source_version"] = "2.1"
source_id["source_id"]["LOCA2-1"]["title"] = "LOCA 2.1 dataset prepared for DRCDP"
# MACA3-0
source_id["source_id"]["MACA3-0"] = {}
source_id["source_id"]["MACA3-0"]["calendar"] = "gregorian"
source_id["source_id"]["MACA3-0"][
    "contact"
] = "John T. Abatzoglou; jabatzoglou@ucmerced.edu"
source_id["source_id"]["MACA3-0"][
    "further_info_url"
] = "https://www.climatologylab.org/maca.html"
source_id["source_id"]["MACA3-0"]["grid"] = "10 x 10 km latitude x longitude"
source_id["source_id"]["MACA3-0"]["grid_label"] = "gn"
source_id["source_id"]["MACA3-0"]["institution_id"] = "UCM-ACSL"
source_id["source_id"]["MACA3-0"][
    "license"
] = "Creative Commons CC0 1.0 Universal Public Domain Dedication"
source_id["source_id"]["MACA3-0"][
    "license_id"
] = "CC0 1.0"  # https://www.climatologylab.org/maca.html#References
source_id["source_id"]["MACA3-0"][
    "license_url"
] = "https://creativecommons.org/publicdomain/zero/1.0/"
source_id["source_id"]["MACA3-0"]["nominal_resolution"] = "10 km"
source_id["source_id"]["MACA3-0"]["product"] = "downscaled-statistical"
source_id["source_id"]["MACA3-0"]["reference"] = " ".join(
    [
        "Abatzoglou, John T., and Timothy J. Brown",
        "(2012) A comparison of statistical downscaling",
        "methods suited for wildfire applications.",
        "International Journal of Climatology, 32 (5),",
        "pp 772-780. https://doi.org/10.1002/joc.2312",
    ]
)
source_id["source_id"]["MACA3-0"]["region"] = "north_america"
source_id["source_id"]["MACA3-0"]["region_id"] = "NAM"
source_id["source_id"]["MACA3-0"][
    "source"
] = "MACA 3.0: Statistically-downscaled climate model projections based on CMIP6"
source_id["source_id"]["MACA3-0"]["source_name"] = "MACA"
source_id["source_id"]["MACA3-0"]["source_version"] = "3.0"
source_id["source_id"]["MACA3-0"]["title"] = "MACA 3.0 dataset prepared for DRCDP"
# STAR-ESDM1-0
source_id["source_id"]["STAR-ESDM1-0"] = {}

source_id["source_id"]["STAR-ESDM1-0"]["calendar"] = "365_day"
source_id["source_id"]["STAR-ESDM1-0"][
    "contact"
] = "Katharine Hayhoe; katharine.hayhoe@ttu.edu"
source_id["source_id"]["STAR-ESDM1-0"][
    "further_info_url"
] = "https://www.depts.ttu.edu/csc/data/"
source_id["source_id"]["STAR-ESDM1-0"]["grid"] = "5 x 5 km latitude x longitude"
source_id["source_id"]["STAR-ESDM1-0"]["grid_label"] = "gn"
source_id["source_id"]["STAR-ESDM1-0"]["institution_id"] = "TTU"
source_id["source_id"]["STAR-ESDM1-0"][
    "license"
] = "Creative Commons Attribution 4.0 International"
source_id["source_id"]["STAR-ESDM1-0"]["license_id"] = "CC BY 4.0"
source_id["source_id"]["STAR-ESDM1-0"][
    "license_url"
] = "https://creativecommons.org/licenses/by/4.0/"
source_id["source_id"]["STAR-ESDM1-0"]["nominal_resolution"] = "5 km"
source_id["source_id"]["STAR-ESDM1-0"]["product"] = "downscaled-statistical"
source_id["source_id"]["STAR-ESDM1-0"]["reference"] = " ".join(
    [
        "Hayhoe, K., Scott-Fleming, I., Stoner, A., and",
        "Wuebbles, D. J. (2024) STAR-ESDM: A generalizable",
        "approach to generating high-resolution climate",
        "projections through signal decomposition.",
        "Earth's Future, 12, e2023EF004107.",
        "https://doi.org/10.1029/2023EF004107",
    ]
)
source_id["source_id"]["STAR-ESDM1-0"]["region"] = "north_america"
source_id["source_id"]["STAR-ESDM1-0"]["region_id"] = "NAM"
source_id["source_id"]["STAR-ESDM1-0"][
    "source"
] = "STAR-ESDM 1.0: Statistically-downscaled climate model projections based on CMIP6"
source_id["source_id"]["STAR-ESDM1-0"]["source_name"] = "STAR-ESDM"
source_id["source_id"]["STAR-ESDM1-0"]["source_version"] = "1.0"
source_id["source_id"]["STAR-ESDM1-0"][
    "title"
] = "STAR-ESDM 1.0 dataset prepared for DRCDP"
source_id


# ### create table_id

# In[14]:


table_id = {}
table_id["table_id"] = ["AP1hr", "APday"]
table_id


# ### create tracking_id

# In[15]:


tracking_id = {}
tracking_id["tracking_id_prefix"] = ["hdl:21.14100"]
tracking_id


# ### write all files out to repo root dir

# In[16]:


files = [
    "DRS",
    "frequency",
    "grid_label",
    "institution_id",
    "license",
    "nominal_resolution",
    "product",
    "realm",
    "region",
    "required_global_attributes",
    "source_id",
    "table_id",
    "tracking_id",
]
for count, name in enumerate(files):
    print(count, name)
    dic = eval(name)
    # write file
    outFile = "".join(["../DRCDP_", name, ".json"])
    with open(outFile, "w") as f:
        json.dump(
            dic, f, ensure_ascii=True, sort_keys=True, indent=4, separators=(",", ":")
        )


# ### create composite institution_id for DRCDP_CV.json

# In[17]:


get_ipython().run_cell_magic('time', '', 'keys = institution_id["institution_id"].keys()\nnewInstId = {}\nfor count, key in enumerate(keys):\n    newInstId[key] = {}\n    tmpStr = "".join([institution_id["institution_id"][key]["name"], " (ROR: ", institution_id["institution_id"][key]["ROR"], ")"])\n    newInstId[key] = tmpStr\nnewInstId\n')


# ### create composite DRCDP_CV.json for CMOR

# In[18]:


get_ipython().run_cell_magic('time', '', 'CV = {}\nCV["CV"] = {}\nCV["CV"]["DRS"] = DRS["DRS"]\nCV["CV"]["activity_id"] = ["DRCDP"]\nCV["CV"]["frequency"] = frequency["frequency"]\nCV["CV"]["grid_label"] = grid_label["grid_label"]\nCV["CV"]["institution_id"] = newInstId\nCV["CV"]["license"] = license["license"]\nCV["CV"]["nominal_resolution"] = nominal_resolution["nominal_resolution"]\nCV["CV"]["product"] = product["product"]\nCV["CV"]["realm"] = realm["realm"]\nCV["CV"]["region"] = region["region"]\nCV["CV"]["required_global_attributes"] = required_global_attributes[\n    "required_global_attributes"\n]\nCV["CV"]["source_id"] = source_id["source_id"]\nCV["CV"]["table_id"] = table_id["table_id"]\nCV["CV"]["tracking_id_prefix"] = tracking_id["tracking_id_prefix"]\n# CV\n# write file\noutFile = "".join(["../Tables/DRCDP_CV.json"])\nwith open(outFile, "w") as f:\n    json.dump(CV, f, ensure_ascii=True, sort_keys=True, indent=4, separators=(",", ":"))\n')

