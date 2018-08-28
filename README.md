# REACH
Data pipeline stages and run scripts for REACH.

Note that this repository is a fork of 
[Wellcome_Dfid_Somalia](https://github.com/AfricasVoices/Wellcome_Dfid_Somalia). 
Migration of this code base to support REACH instead of Wellcome is still a work in progress.

## Usage
### Prerequisites
#### Tools
Install Python 3.6+, Pipenv, and Docker.

#### SMS Fetcher
The data fetching stages of the pipeline require access to a local copy of the 
[RapidPro fetcher](https://github.com/AfricasVoices/RapidProExperiments) project.
To configure this:
 
1. Clone that repository to your local system:

   `$ git clone https://github.com/AfricasVoices/RapidProExperiments.git`
   
1. Checkout the appropriate commit for this project:

   `$ git checkout master`  # TODO: Tag RapidProExperiments appropriately
   
1. Install project dependencies:
   ```bash
   $ cd RapidProExperiments
   $ pipenv --three
   $ pipenv sync
   ```

### Running
#### SMS Fetcher
1. Create an empty data directory somewhere on the file system.

1. In this directory, create a new, empty phone number UUID table: `$ echo "{}" > <json-table-file-path>`.

1. Change into the RapidProExperiments directory.

1. To export data, run `$ pipenv run python fetch_runs.py`, setting arguments as described in the sections below,
   program `--help`, and the README for that project.
   
#### Messages Pipeline (for Radio Show Answers)
Run the RapidPro fetcher in `all` mode on the activation flow for S06E01, for which this stage is (temporarily) hard-coded
(i.e. set the `<flow-name>` argument of `fetch_runs.py` to `wt_s06e1_activation`).

In this repository, change into `messages/` and run `$ sh docker-run.sh <args>`, setting `<input>` to the json 
file produced by the SMS fetch stage.

This will convert a list of TracedData items to a more user-friendly CSV.

#### Survey Pipeline (for Demographics)
Run the RapidPro fetcher in `latest-only` mode on a demographic flow for Wellcome (e.g. `wt_demog_1`).

In this repsoitory, change into `regex_tester/` and run `$ sh docker-run.sh <args>`, setting `<input>` to the json
file produced by the SMS fetch stage.

This will apply the specified regex to each value for the given key in the list of TracedData objects, 
and produce a CSV file which lists whether each (de-duplicated) entry matched or not.

