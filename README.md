# FUCCI Analysis Pipeline

## Setup
This project uses [Conda](https://docs.conda.io/projects/conda/en/latest/user-guide/index.html) for dependency management. To [create a Conda env](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-from-an-environment-yml-file) with the appropriate packages and environment variables, run `conda env create -f environment.yml`, then run `conda activate fucci_analysis` to use it.


## Running the data annotation + plot UIs

This package contains two UIs: the Plate and Plot UI.

The Plate UI enables annotation of the well numbers with condition information and can be run with `python plate.py`. It accepts Excel files and produces CSVs. The Plot UI takes a CSV and produces the corresponding plots and statistics on the basis of a number selectable options. It can be run with `python plot.py`.

Both the plate and plot UI script also accept any number of filenames as command line arguments, for instance `python fucci_analysis/plate.py ~/OneDrive/my_folder/file1.xlsx ~/OneDrive/my_folder/file2.xlsx`. If no filenames are given, the UI will prompt you with a file selector.


## Testing
There are a handful of tests written using [pytest](https://docs.pytest.org/en/stable/). These can be run using `pytest`. The tests are not exhaustive as there is no good automated testing framework for the tkinter UI. Update with caution.