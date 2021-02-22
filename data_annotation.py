from datetime import datetime
import pandas as pd
import os

HEADERS = ['PlateNum', 'WellNum', 'Day', 'Count', 'Marker']


class AnnotatedData:
    WELL_NUMS = 96

    def __init__(self, filepaths, frames=None):
        self.load_files(filepaths, frames)
        self.set_marker()
        self.set_total_and_cell_percent()

    def load_files(self, filepaths, frames):
        self.directory = os.path.commonpath(
            [os.path.dirname(path) for path in filepaths]
        )
        filetypes = [path.split('.')[-1] for path in filepaths]
        data = []
        if all([filetype == 'xlsx' for filetype in filetypes]):
            for path in filepaths:
                x = pd.ExcelFile(path)
                # Some files have the headers specified but others
                # don't. Handle this by trying first to parse without
                # headers and then seeing if the headers are in the
                # first row.
                first_row = x.parse(
                    "Sheet1",
                    header=None,
                    names=HEADERS,
                    nrows=1
                )
                if set(HEADERS).intersection(set(first_row.loc[0].values)):
                    m = x.parse(
                        "Sheet1",
                        header=0
                    )
                else:
                    m = x.parse(
                        "Sheet1",
                        header=None,
                        names=HEADERS
                    )
                if "DayNum" in m.columns:
                    m.rename(columns={"DayNum": "Day"}, inplace=True)

                if frames:
                    m['Frame'] = frames[path]
                else:
                    m['Frame'] = None

                data.append(m)

        elif all([filetype == 'csv' for filetype in filetypes]):
            for path in filepaths:
                m = pd.read_csv(path)
                data.append(m)
        else:
            raise ValueError("Unhandled filetype (not .xlsx or .csv)")

        self.dataframe = pd.concat(data)
        self.dataframe.reset_index(drop=True, inplace=True)

        if 'Condition' not in self.dataframe.columns:
            self.dataframe['Condition'] = None

        if 'PlateRow' not in self.dataframe.columns:
            self.dataframe['PlateRow'] = None

        if 'PlateColumn' not in self.dataframe.columns:
            self.dataframe['PlateColumn'] = None

    def start_day(self):
        return self.dataframe['Day'].min()

    def end_day(self):
        return self.dataframe['Day'].max()

    def plate_nums(self):
        plate_nums = self.dataframe['PlateNum'].unique()
        plate_nums.sort()
        return plate_nums

    def get_frames(self):
        frames = self.dataframe['Frame'].unique()
        frames.sort()
        return frames

    def get_conditions(self):
        conditions = self.dataframe['Condition'].unique()
        conditions.sort()
        return conditions

    def set_condition(self, condition, well_num,
                      plate_num, plate_column, plate_row):
        query_str = f'WellNum == {well_num} & \
            PlateNum == {plate_num}'
        query_index = self.dataframe.query(query_str).index
        self.dataframe.loc[
            query_index, ['Condition', 'PlateRow', 'PlateColumn']
        ] = [condition, plate_row, plate_column]

    def set_marker(self):
        self.dataframe['Marker'] = self.dataframe['Marker'].replace(
            [0, 1, 2], ['RFP', 'YFP', 'Overlap']
        )

    def set_total_and_cell_percent(self):
        # write in total cell count
        self.dataframe['Total'] = 0

        for _, rows in self.dataframe.groupby(['PlateNum', 'WellNum', 'Day']):
            total = rows['Count'].sum()
            self.dataframe.loc[rows.index, 'Total'] = total

        # write in cell percentages based on totals
        percent = self.dataframe['Count'] / self.dataframe['Total']
        self.dataframe['Cell_percent'] = percent

    def save(self):
        if (self.dataframe['Condition'] == None).any():
            raise DataValidationError("Missing condition assignments")
        timestamp = datetime.now().strftime('%Y%m%d%M%S')
        for frame in self.get_frames():
            path = os.path.join(
                self.directory,
                f'frame_m{frame}_processed_data_{timestamp}.csv'
            )
            data = self.dataframe[self.dataframe['Frame'] == frame]
            data.to_csv(
                path_or_buf=path,
                index=None,
                header=True
            )


class DataValidationError(RuntimeError):
    '''Used for issues with DataAnnotation'''
