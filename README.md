# FUCCI Analysis Pipeline

## Setup
This project uses [Poetry](https://python-poetry.org/) to handle dependencies and testing. If you don't have Poetry installed, run `pip install poetry` (docs [here](https://python-poetry.org/docs/)).

To install the necessary dependencies, run `poetry install`.

#### Debugging setup issues
- You may run into an error of the form `“The headers or library files could not be found for jpeg`. This is because one of the dependencies for the Pillow package, `libjpeg`, is not installed. On MacOS, use [Homebrew](https://brew.sh/) to get the package and try again: `brew install libjpeg`.

If you are installing on a Macboook, you may need to follow [these extra steps](https://github.com/scipy/scipy/issues/13102#issuecomment-767502377).

## Running the data annotation UI

Because all the dependencies are handled through Poetry, running the script requires prefacing any commands with `poetry run`. For instance, opening the plate annotation UI from the top level of this project would mean running `poetry run python fucci_analysis/plate.py`

The plate UI script also accepts any number of filenames as command line arguments, for instance `poetry run python fucci_analysis/plate.py ~/OneDrive/my_folder/file1.xlsx ~/OneDrive/my_folder/file2.xlsx`. If no filenames are given, the UI will prompt you with a file selector.

## Testing
There are a handful of tests written using [pytest](https://docs.pytest.org/en/stable/). These can be run using `poetry run pytest`. The tests are not exhaustive as there is no good automated testing framework for the tkinter UI. Update with caution.