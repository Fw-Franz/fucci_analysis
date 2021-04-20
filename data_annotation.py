from datetime import datetime
from main import TOTAL_NORM, RELATIVE_NORM, NORMALIZED_METHOD, RAW_METHOD, FOLD_CHANGE_METHOD
import pandas as pd
import os

HEADERS = ['PlateNum', 'WellNum', 'Day', 'Count', 'Marker']


class AnnotatedData:
    WELL_NUMS = 96

    def __init__(self, filepaths):
        self.filepaths = filepaths
        self.directory = os.path.commonpath(
            [os.path.dirname(path) for path in filepaths]
        )

    def load_annotated_files(self):
        ''' Load assuming you have already annotated everything'''
        data = []
        for path in self.filepaths:
            m = pd.read_csv(path)
            m['Filepath'] = path
            data.append(m)

        self.dataframe = pd.concat(data)
        self.dataframe.reset_index(drop=True, inplace=True)

    def load_unannotated_files(self, frames):
        ''' Load assuming you are about to annotate the files'''
        data = []
        for path in self.filepaths:
            file_extension = os.path.splitext(path)[-1]
            if file_extension == '.xlsx':
                m = self.load_xlsx(path)
            elif file_extension == '.csv':
                m = self.load_csv(path)
            else:
                raise ValueError("Unhandled filetype (not .xlsx or .csv)")

            if "DayNum" in m.columns:
                m.rename(columns={"DayNum": "Day"}, inplace=True)

            m['Frame'] = frames[path]
            data.append(m)

        self.dataframe = pd.concat(data)
        self.dataframe.reset_index(drop=True, inplace=True)

        columns = ['Condition', 'PlateRow', 'PlateColumn', 'Date']
        for column in columns:
            if column not in self.dataframe.columns:
                self.dataframe[column] = None

        self.set_marker()
        self.set_total_and_cell_percent()

    @staticmethod
    def load_xlsx(path):
        x = pd.ExcelFile(path)
        # Some files have the headers specified but others
        # don't. Handle this by trying first to parse without
        # headers and then seeing if the headers are in the
        # first row.
        first_row = x.parse(
            header=None,
            names=HEADERS,
            nrows=1
        )
        if set(HEADERS).intersection(set(first_row.loc[0].values)):
            return x.parse(
                header=0
            )
        else:
            return x.parse(
                header=None,
                names=HEADERS
            )

    @staticmethod
    def load_csv(path):
        # Some files have the headers specified but others
        # don't. Handle this by trying first to parse without
        # headers and then seeing if the headers are in the
        # first row.
        first_row = pd.read_csv(
            path,
            header=None,
            names=HEADERS,
            nrows=1
        )
        if set(HEADERS).intersection(set(first_row.loc[0].values)):
            return pd.read_csv(
                path,
                header=0
            )
        else:
            return pd.read_csv(
                path,
                header=None,
                names=HEADERS
            )

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

    def get_dates(self):
        dates = self.dataframe['Date'].unique()
        dates.sort()
        return dates

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

    def set_date(self, date):
        self.dataframe['Date'] = date

    def set_normalization(self, stats_var, control_condition):
        total_normalized = self.normalization_colname(TOTAL_NORM, NORMALIZED_METHOD, stats_var, control_condition)
        relative_normalized = self.normalization_colname(RELATIVE_NORM, NORMALIZED_METHOD, stats_var, control_condition)
        total_fold_change = self.normalization_colname(TOTAL_NORM, FOLD_CHANGE_METHOD, stats_var, control_condition)
        relative_fold_change = self.normalization_colname(RELATIVE_NORM, FOLD_CHANGE_METHOD, stats_var, control_condition)
        self.dataframe[[total_normalized, relative_normalized, total_fold_change, relative_fold_change]] = 0.0

        groups = {k: v for k, v in self.dataframe.groupby(['Date', 'Day', 'Condition', 'Marker'])}
        for (date, day, condition, marker), group in groups.items():
            idx = group.index
            start_day_group = groups[(date, self.start_day(), condition, marker)]
            control_condition_group = groups[(date, day, control_condition, marker)]
            control_start_day_group = groups[(date, self.start_day(), control_condition, marker)]

            group = group.reset_index(drop=True)
            start_day_group = start_day_group.reset_index(drop=True)
            control_condition_group = control_condition_group.reset_index(drop=True)
            control_start_day_group = control_start_day_group.reset_index(drop=True)

            group[total_normalized] = group[stats_var] / start_day_group[stats_var]
            group[relative_normalized] = (group[stats_var] - start_day_group[stats_var]) / start_day_group[stats_var]
            group[total_fold_change] = group[total_normalized] / (control_condition_group[stats_var].mean() / control_start_day_group[stats_var].mean())
            group[relative_fold_change] = group[relative_normalized] / ((control_condition_group[stats_var].mean() - start_day_group[stats_var].mean()) / control_start_day_group[stats_var].mean())

            for k, j in enumerate(idx):
                self.dataframe[total_normalized].iloc[j] = group[total_normalized].iat[k]
                self.dataframe[relative_normalized].iloc[j] = group[relative_normalized].iat[k]
                self.dataframe[total_fold_change].iloc[j] = group[total_fold_change].iat[k]
                self.dataframe[relative_fold_change].iloc[j] = group[relative_fold_change].iat[k]

    @staticmethod
    def normalization_colname(normalization_type, analyze_method, stats_var, control_condition):
        if analyze_method == RAW_METHOD:
            return stats_var
        colname = f'{stats_var}_{normalization_type}_{analyze_method}_norm'
        if analyze_method == FOLD_CHANGE_METHOD:
            colname = f'{colname}_{control_condition}'
        return colname

    def save(self):
        if self.dataframe['Date'].isnull().any():
            raise DataValidationError("Missing date assignment")
        if self.dataframe['Condition'].isnull().any():
            raise DataValidationError("Missing condition assignments")
        if 'Filepath' in self.dataframe.columns:
            for path in list(self.dataframe['Filepath'].unique()):
                data = self.dataframe.query(f'Filepath == "{path}"').drop(columns='Filepath')
                data.to_csv(
                    path_or_buf=path,
                    index=None,
                    header=True
                )
        else:
            for frame in self.get_frames():
                date_str = "_".join(list(self.get_dates()))
                path = os.path.join(
                    self.directory,
                    f'frame_m{frame}_processed_data_{date_str}.csv'
                )
                data = self.dataframe.query(f'Frame == {frame}')
                data.to_csv(
                    path_or_buf=path,
                    index=None,
                    header=True
                )


class DataValidationError(RuntimeError):
    '''Used for issues with DataAnnotation'''
