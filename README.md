# Project REACH
Data pipeline for REACH/DAAP.

This pipeline fetches all project data from a Rapid Pro instance, and processes it to produce CSV files suitable
for downstream analysis.

## Pre-requisites
Before the pipeline can be run, the following tools must be installed:
 - Docker
 - Bash
 
Development requires the following additional tools:
 - Python 3.6+
 - pipenv
 - git

## Usage
Running the pipeline requires (1) creating a phone number <-> UUID table to support de-identification of 
respondents, (2) fetching all the relevant data from Rapid Pro, and (3) processing the raw data to
produce the outputs required for coding and then for analysis. 

To simplify the configuration and execution of these stages, this project includes a `run_scripts`
directory, which contains shell scripts for driving each of the stages. 
More detailed descriptions of the functions of each of those stages, and instructions for using
the run scripts, are provided below. 

### 1. Phone Number <-> UUID Table
First, create an empty phone number <-> UUID table by running the following command in 
the `run_scripts` directory:

```
$ ./1_create_uuid_table.sh <data-root> 
```

where `data-root` is an absolute path to the directory in which all pipeline data should be stored. 
The UUID table will be saved to a file in the directory `<data-root>/UUIDs`.

### 2. Fetch Raw Data
Next, fetch all the raw data required by the pipeline from Rapid Pro by running the following command in 
the `run_scripts` directory:

`$ ./2_fetch_raw_data.sh <user> <rapid-pro-root> <rapid-pro-server> <rapid-pro-token> <data-root>`.

where:
 - `user` is the identifier of the person running the script, for use in the TracedData Metadata 
   e.g. `user@africasvoices.org`
 - `rapid-pro-root` is an absolute path to the directory to store a local clone of 
   [RapidProTools](https://github.com/AfricasVoices/RapidProTools) in.
   The RapidProTools project hosts the re-usable RapidPro data fetchers.
   The exact version required by this project is checked out automatically.
 - `rapid-pro-server` is the root address of the RapidPro server to retrieve data from e.g. `https://app.rapidpro.io`.
 - `rapid-pro-token` is the access token for this instance of RapidPro. The access token may be found by logging into 
   RapidPro's web interface, then navigating to your organisation page (via the button in the top-right), then copying
   the hexadecimal string given after "Your API Token is ..."
 - `data-root` is an absolute path to the directory in which all pipeline data should be stored.
   Raw data will be saved to TracedData JSON files in `<data-root>/Raw Data`. 

### 3. Generate Outputs
Finally, process the raw data to produce outputs for The Interface, ICR, Coda, and messages/individuals CSVs for 
final analysis, by running the following command in the `run_scripts` directory.

```
$ ./3_generate_outputs.sh <user> <data-root>
```

where:
 - `user` is the identifier of the person running the script, for use in the TracedData Metadata 
   e.g. `user@africasvoices.org`
 - `data-root` is an absolute path to the directory in which all pipeline data should be stored.
   Updated Coda files containing new data to be coded will be saved in `<data-root>/Raw Data`.
   All other output files will be saved in `<data-root>/Outputs`.
   
After the first run, the generated Coda files may be loaded into Coda and labelled. 
If this is done, the manually-labelled Coda files must be made available to the pipeline before re-running, otherwise
the new Coda files will require the same messages to be labelled again. 
To make the labelled Coda files available to the pipeline, append `_coded` to the original file name
(e.g. `District.csv` would become `District_coded.csv`), and save to `<data-root>/Coded Coda Files`.
