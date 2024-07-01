# Test Site Modeling Script Explanation

---

## Data Preparation

The script reads in two datasets:

* `test_sites`: dummy sites with characteristics (elevation, slope, wetness)
* `known_sites`: known dig sites  with same characteristics

## Cleaning the Data

The script cleans and preprocesses the data by:

* Merging columns together
  * Coalescing WAW (Water and Wetness) columns into a single column
  * Merging elevation column in known_sites dataset (using literature values if available)
* Converting data types to match expected formats

## Labeling the Data

The script applies rules to label each row in `test_sites` as "dig site" or not using the `not_site_criteria` function. The criteria for a site to be labeled as not a possible dig site are:

* Elevation > 400m
* Distance to chert > 20km
* Distance to coast > 6km

## Mixing the Data

The script adds 1% of non-dig sites to known dig sites, as the model needs to identify traits of both types of locations.

## Running Simulations

The script runs multiple simulations using XGBoost Python package. The model trains on columns:

* Elevation
* Wetness
* Temp
* Slope
* NEAR_DIST_Chert
* NEAR_DIST_Canals
* NEAR_DIST_River_Net
* NEAR_DIST_Coastal

The script runs 5000 simulations, noting the number of times each site is picked. This was chosen to account for model randomness and data variance. The linear classifier from XGBoost was chosen over something like a Neural Network due the tendancy for NNs to overfit the data. The XGBoost model is a good balance between accuracy and generalization. We wanted to avoid overfitting the data as much as possible and also some variance in the results as the input data isn't perfect.

## Combining Results

The script combines simulation results into a single dataset, `collection_df`.

## Grouping and Counting

The script groups data by "OBJECTID" (unique identifier) and counts predictions for each site.

## Saving the Results

The script saves the final dataset to two files:

* `mass_test.parquet`: individual simulations
* `mass_test_grouped.parquet`: grouped data with count information (also saved in CSV format)
