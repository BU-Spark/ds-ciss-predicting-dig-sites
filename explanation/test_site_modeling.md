# Explanation of Test Site Modeling Script

1. **Data preparation**:
    * The script reads in two datasets:
        * `test_sites`: This dataset contains evenly spread out dummy sites and their characteristics (e.g., elevation, slope, wetness).
        * `known_sites`: This dataset contains known dig sites with the same characteristics.
2. **Cleaning the data**:
    * The script cleans and preprocesses the data by:
        * Merging several columns together
            * The WAW (or Water and Wetness) columns are coalesced into a single column
            * The elevation column in the known_sites dataset is also coalesced together, but if the site had an elevation noted in literature, that value is used
        * Converting data types to match the expected formats
3. **Labeling the data**: 
    * The script applies a set of rules to label each row in the `test_sites` dataset as either "dig site" or not (i.e., not a dig site). This is done using the `not_site_criteria` function.
        * The current criteria for a site to be labeled as not a possible dig site are as follows:
            * Elevation > 400m
            * Distance to chert > 20km
            * Distance to the coast > 6km
4. **Mixing the data**
    * The script selects 1% of the test sites that were labeled as not a possible dig site and adds them to the list of known dig sites.
    * This is done because the model needs to be able to identify the traits of locations that are not dig sites as well as those that are.
5. **Running simulations**: The script runs multiple simulations using the XGBoost Python package.
    * Using the following columns, the script trains the model to predict whether a site is a dig site or not:
        * Elevation
        * Wetness
        * Temp
        * Slope
        * NEAR_DIST_Chert
        * NEAR_DIST_Canals
        * NEAR_DIST_River_Net
        * NEAR_DIST_Coastal
    * The simulations are run a total of 5000 times and the number of times that each site is picked is noted.
        * It was decided to run the model and data mixing many times in order to account for the randomness of the model and the data.
        * 5000 was picked arbitrarily, but it was decided that this number was large enough to get a good idea of the distribution of the data. Additionally, any more rounds and the script would take too long to run (i.e. >1hr).
6. **Combining results**: The script combines the results from all simulations into a single dataset, `collection_df`.
7. **Grouping and counting**: The script groups the data by "OBJECTID" (a unique identifier for each dig site) and counts the number of predictions for each site.
8. **Saving the results**: The script saves the final dataset to two files:
    * `mass_test.parquet`: This file contains all the individual simulations.
    * `mass_test_grouped.parquet`: This file contains the grouped data with count information.
        * The grouped data is also stored in a CSV format for easier viewing.
