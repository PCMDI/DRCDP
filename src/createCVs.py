import json


# read data from local (ensuring a pull has occurred to sync with main)
f = open('../DRCDP_institution_id.json','r')
institution_id = json.load(f)

with open('../DRCDP_institution_id.json','r') as f: institution_id = json.load(f)
with open('../DRCDP_source_id.json','r') as f: source_id = json.load(f)

# add new institution_id
key = 'NCAR'
institution_id['institution_id'][key] = {}
institution_id['institution_id'][key][ 'contact' ] = 'Samantha Hartke; hartke@ucar.edu'
institution_id['institution_id'][key][ 'name' ] = 'National Center for Atmospheric Research, Boulder, CO, USA'
#institution_id['institution_id'][key]['ROR'] = '00d9ah105'
#institution_id['institution_id'][key]['URL'] = 'https://www.climatologylab.org'

# add new source_id
key = 'GARD-LENS-1-0'
source_id['source_id'][key] = {}
source_id['source_id'][key]['calendar'] = 'standard'
source_id['source_id'][key]['contact'] = 'Samantha Hartke; hartke@ucar.edu'
source_id['source_id'][key]['further_info_url'] = 'https://opensky.ucar.edu/islandora/object/articles%3A42362'
source_id['source_id'][key]['grid'] = '5 x 5 km latitude x longitude'
source_id['source_id'][key]['grid_label'] = 'gn'
source_id['source_id'][key]['institution_id'] = 'NCAR'
source_id['source_id'][key][ 'license' ] = 'Creative Commons Attribution 4.0 International'
source_id['source_id'][key]['license_id'] = 'CC BY 4.0'
source_id['source_id'][key][ 'license_url' ] = 'https://creativecommons.org/licenses/by/4.0/'
source_id['source_id'][key]['nominal_resolution'] = '5 km'
source_id['source_id'][key]['product'] = 'downscaled-statistical'
source_id['source_id'][key]['reference'] = ' '.join(
    ['Hartke, S.H., Newman, A.J., Gutmann, E. et al. GARD-LENS: A downscaled large ensemble dataset for understanding future climate and its uncertainties. Sci Data 11, 1374 (2024). https://doi.org/10.1038/s41597-024-04205-z' ]
)
source_id['source_id'][key]['region'] = 'north_america'
source_id['source_id'][key]['region_id'] = 'NAM'
source_id['source_id'][key][ 'source' ] = 'GARD-LENS-1-0: Statistically-downscaled climate model projections based on CMIP6'
source_id['source_id'][key]['source_name'] = 'GARD-LENS'
source_id['source_id'][key]['source_version'] = '1.0'
source_id['source_id'][key]['title'] = 'GARD-LENS-1-0 dataset prepared for DRCDP'

# overwrite existing files
# write files
outFile = ''.join(['../DRCDP_institution_id.json'])
with open(outFile, 'w') as f:
    json.dump(institution_id, f, ensure_ascii=True, sort_keys=True, indent=4, separators=(',', ':'))
outFile = ''.join(['../DRCDP_source_id.json'])
with open(outFile, 'w') as f:
    json.dump(source_id, f, ensure_ascii=True, sort_keys=True, indent=4, separators=(',', ':'))

# overwrite DRCDP_CV.json with new entries
f = open('../Tables/DRCDP_CV.json','r')
CV = json.load(f)
CV['CV']['institution_id'] = institution_id['institution_id']
CV['CV']['source_id'] = source_id['source_id']

# overwrite DRCDP_CV.json
outFile = ''.join(['../Tables/DRCDP_CV.json'])
with open(outFile, 'w') as f:
    json.dump(CV, f, ensure_ascii=True, sort_keys=True, indent=4, separators=(',', ':'))

