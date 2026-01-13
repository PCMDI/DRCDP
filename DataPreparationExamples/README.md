## Preparing DRCDP data for ESGF publication (WORK-IN-PROGRESS DRAFT!)

Draft [DRCDP](https://docs.google.com/document/d/1CEhmrHD9D0fq98UlcPus8V0Vf9paB5M4/edit) data specifications have been established for data technically aligned with other Earth System Grid Federation (ESGF) projects including [CMIP](https://zenodo.org/records/12768887), [CORDEX](https://zenodo.org/records/10961069), and [obs4MIPs](https://zenodo.org/records/11500474). Here, we provide guidance to help data providers generate compliant data using these specifications.  


### Nuts and bolts:

- Contributors must register their datasets by [submitting an issue](https://github.com/PCMDI/DRCDP/issues/new/choose) on this DRCDP GitHub repository and filling out the provided template.  

- We recommend data providers prepare their data using Python so that they can more readily leverage the resources described below.

- We recommend using [Xarray](https://docs.xarray.dev) as in the examples provided below, and [xCDAT](https://xcdat.readthedocs.io) to generate coordinate bounds.    

- Use of the [Climate Model Output Writer (CMOR)](https://cmor.llnl.gov/) is required to ensure alignment with other ESGF projects.
     
The easiest way to configure a suitable computing environment is via the [conda package manager](https://docs.conda.io/en/latest/), [Xarray](https://anaconda.org/conda-forge/xarray), [xCDAT](https://anaconda.org/conda-forge/xcdat) and [CMOR](https://anaconda.org/conda-forge/cmor) can be obtained and included in a common environment. 

## How to:  

The recipe below describes the process of preparing a DRCDP-compliant dataset. This typically involves copying information from the provided demos and modifying it as necessary to prepare a new DRCDP-compliant dataset. By preparing a simple python script (example discussed in demo identified below) and an input JavaScript Object Notation (JSON) file, CMOR is used to prepare a DRCDP-compliant dataset.

### Recipe:

1. **Register a new source_id**, if it does not already exist. An issue can be submitted on this GitHub repo ([here](https://github.com/PCMDI/DRCDP/issues/new/choose)) with a proposed "source_id" and other key registered content (RC). A member of the team will quickly review this information and enter it into the database of source_id's or propose an alternative if the proposed identifier does not conform to the data specifications. When opening an issue, a template is provided, so one needs to replace the information in the example (GPCP) with their own proposed source_id. The source_id is intended to identify the product/version and generally closely resembles an existing identifier but may be slightly modified to be consistent with CMIP/obs4MIPs conventions. For example: A compliant source_id for "GPCP v2.4" is "GPCP-2-4". More information on the guidelines for constructing a source_id is available in Table 1 of the obs4MIPs data specifications (see [here](https://doi.org/10.5281/zenodo.11500474)). 

2. **Prepare an input table for running CMOR** (e.g., see [here](https://github.com/PCMDI/DRCDP/blob/main/DataPreparationExamples/LOCA2/LOCA2_CMIP6_input.json)). The simplest thing to do is to save this file, rename it, and replace the demo content with the relevant information for a new source_id or dataset. Typically, this involves only making changes to the following attributes: "contact", "grid", "grid_label", "institution_id", "nominal_resolution", "references", "outpath", "source_id", "title", "variant_info" and "variant_label". For explanations of these attributes, see the obs4MIPs data specifications (see [here](https://doi.org/10.5281/zenodo.11500474)).

3. **Prepare a Python script for reading in data and writing with CMOR**. This is the most time consuming aspect of preparing a DRCDP-compliant dataset, but examples provided on this repo (see [here](https://github.com/PCMDI/DRCDP/tree/main/DataPreparationExamples)) help to streamline the process. It involves preparing a simple Python script to read the original data and rewrite it using CMOR. As with the steps before, one can start by downloading a demo python script (see examples), renaming, and modifying as needed.

4. **Process and generation DRCDP compliant data by executing your Python script.** The processed data will be located in a directory defined in the input_table: outpath + output_path_template, the former being the base directory (where the user wants to output the data). The latter being a directory template explicitly defined for DRCDP (<activity_id>/<institution_id>/<source_id>/<variable_id>/<grid_label>/).

5. **Contact the DRCDP team with any questions** with the above and to arrange verification and data transfer for ESGF publication.


##### Document version: 18 June 2025
