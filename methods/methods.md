# Methods

## The Basis of Analysis

* Currently following the steps taken by Stephanie R. Rogers and Claude Collet from the University of Fribourg, Switzerland, and Ralph Lugon from the University of Applied Sciences and Arts, Western Switzerland in their paper titled *Least Cost Path Analysis for Predicting Glacial Archaeological Site Potential in Central Europe*. The paper was published as part of the journal *Across Space and Time* from the 41st Conference on Computer Applications and Quantitative Methods in Archaeology in 2013 (on pages 261 to 275).
* To summarize the abstract of their paper, they calculated the Least Cost Paths (LCPs) between archaeologically significant locations in Switzerland and Italy. They then analyzed the LCPs which eventually led to the discovery of an artifact from the Bronze Age (~2,800 years BP or 850 BCE/BC).

## Steps Taken

1. Downloading and understanding the data
    * The environmental data we recieved needs to be unzipped and organized in a way that is easy to access.
    * The data about the currently known sites needed to be "normalized" as the coordinates where in different formats (decimal vs dmh).
        * we used Python to do the normalization but due to an issue w/ my computer, I was unable to backup the code. However I did luckily send the data on Slack so I did not need to reproduce everything. If the original code is needed, I can rewrite it.

2. Preparing the data
    * This step was simply to import all of the data into ArcGIS Pro and make sure that everything worked.

3. Analyzing the data
    * This step was to run the LCP analysis on the data and see if we could find any patterns.
        * Currently, we have been able to create a distance path raster, but have been unsuccessful in my attempts to use the raster to find optimal paths.
    * Using these Tool References from ArcGIS
        * [Path Distance (Spatial Analyst)](https://pro.arcgis.com/en/pro-app/latest/tool-reference/spatial-analyst/path-distance.htm)
            * This tool is deprecated, but the replacement for it performs differently and I have not been able to get it to work.
        * [Optimal Path As Raster (Spatial Analyst)](https://pro.arcgis.com/en/pro-app/latest/tool-reference/spatial-analyst/optimal-path-as-raster.htm)