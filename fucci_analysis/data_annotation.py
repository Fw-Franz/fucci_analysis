from datetime import datetime
import pandas as pd
import os

HEADERS = ['PlateNum', 'WellNum', 'Day', 'Count', 'Marker']


class AnnotatedData:
    WELL_NUMS = 96

    def __init__(self, filepaths, frame=None, percents=None):
        self.load_files(filepaths)
        self.set_frame(frame)
        self.set_marker()
        self.set_percents(percents)
        self.set_total_and_cell_percent()

    def load_files(self, filepaths):
        self.directory = os.path.commonpath(filepaths)
        filetypes = [path.split('.')[-1] for path in filepaths]
        frames = []
        if all([filetype == 'xlsx' for filetype in filetypes]):
            for path in filepaths:
                x = pd.ExcelFile(path)
                # Some files have the headers specified but others
                # don't. Handle this by trying first to parse without
                # headers and then seeing if the headers are in the
                # first row.
                m = x.parse(
                    "Sheet1",
                    header=None,
                    names=HEADERS
                )
                if set(HEADERS).intersection(set(m.loc[0].values)):
                    m = x.parse(
                        "Sheet1",
                        header=0
                    )
                if "DayNum" in m.columns:
                    m.rename(columns={"DayNum": "Day"}, inplace=True)

                frames.append(m)

        elif all([filetype == 'csv' for filetype in filetypes]):
            for path in filepaths:
                m = pd.read_csv(path)
                frames.append(m)
        else:
            raise ValueError("Unhandled filetype (not .xlsx or .csv)")

        self.dataframe = pd.concat(frames)
        self.dataframe.reset_index(drop=True, inplace=True)

    def plate_nums(self):
        return self.dataframe['PlateNum'].max()

    def set_condition(self, condition, well_num, plate_num):
        if 'Condition' not in self.dataframe.columns:
            self.dataframe['Condition'] = None

        # it is easier to deal with string identifiers on the frontend
        # so coerce values here
        if condition == 'None':
            condition = None

        query_str = f'WellNum == {well_num} & \
            PlateNum == {plate_num}'
        query_index = self.dataframe.query(query_str).index
        self.dataframe.loc[query_index, 'Condition'] = condition

    def set_percents(self, percents):
        if percents is None:
            return

        self.percents = percents
        self.dataframe['Percent'] = percents[0]

        # TODO: What is the deal with this?
        # for well in range(1, self.WELL_NUMS + 1):
        #     query_str = f'WellNum == {well}'
        #     my_query_index = self.dataframe.query(query_str).index
        #     x = self.dataframe.columns.get_loc('Percent')
        #     if np.mod(int((well-1)/6),len(percents)):
        #         self.dataframe.iloc[my_query_index, x] = 'low'
        #     else:
        #         self.dataframe.iloc[my_query_index, x] = 'high'

    def set_frame(self, frame):
        if frame is None:
            return

        self.frame = frame
        self.dataframe['Frame'] = frame
        print(f'Changed frame to {self.frame}')

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
        if not self.frame:
            raise DataValidationError('Missing frame assignment')
        if not (self.dataframe['Condition'] == None).all():
            raise DataValidationError("Missing condition assignments")
        timestamp = datetime.now().strftime('%Y%m%d%M%S')
        path = os.path.join(
            self.directory,
            f'frame_m{self.frame}_processed_data_{timestamp}.csv'
        )
        self.dataframe.to_csv(
            path_or_buf=path,
            index=None,
            header=True
        )
        return path


class DataValidationError(RuntimeError):
    '''Used for issues with DataAnnotation'''
