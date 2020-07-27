# covid_nhse
Analysis of NHS England Covid19 hospital deaths by date of reporting and date of death.

To use, simply run `main.py` after installing the required packages in your Python3 environment.

The script creates a new `data` folder and downloads Excel spreadsheets from [NHS England](https://www.england.nhs.uk/statistics/statistical-work-areas/covid-19-daily-deaths/).

After reading these files, it outputs graphs of NHS hospital death numbers in the seven NHS England regions, as well as for England as a whole. These are stored in the `out` directory created by the script.
