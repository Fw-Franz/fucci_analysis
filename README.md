# FUCCI Analysis Pipeline

### Setup
This project uses [Poetry](https://python-poetry.org/) to handle dependencies and testing. If you don't have Poetry installed, run `pip install poetry` (docs [here](https://python-poetry.org/docs/)).

To install the necessary dependencies, run `poetry install`.

### Running the data annotation UI

Because all the dependencies are handled through Poetry, running the script requires prefacing any commands with `poetry run`. For instance, opening the plate annotation UI from the top level of this project would mean running `poetry run python fucci_analysis/plate.py`

The plate UI script also accepts any number of filenames as command line arguments, for instance `poetry run python fucci_analysis/plate.py ~/OneDrive/my_folder/file1.xlsx ~/OneDrive/my_folder/file2.xlsx`. If no filenames are given, the UI will prompt you with a file selector.

## Testing
There are a handful of tests written using [pytest](https://docs.pytest.org/en/stable/). These can be run using `poetry run pytest`. The tests are not exhaustive as there is no good automated testing framework for the tkinter UI. Update with caution.