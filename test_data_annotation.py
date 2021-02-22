import data_annotation
import os
import pandas as pd


def test_set_conditions():
    base_directory = os.path.join(os.getcwd(), "test_data")
    filepaths = [os.path.join(base_directory, 'test_set_conditions.xlsx')]

    target = pd.DataFrame(data={
        'PlateNum': {0: 1, 1: 1, 2: 2, 3: 2},
        'WellNum': {0: 1, 1: 1, 2: 1, 3: 1},
        'Day': {0: 0, 1: 1, 2: 0, 3: 1},
        'Count': {0: 29, 1: 17, 2: 14, 3: 22},
        'Marker': {0: 'RFP', 1: 'RFP', 2: 'RFP', 3: 'RFP'},
        'Condition': {0: 'Foo', 1: 'Foo', 2: 'Bar', 3: 'Bar'},
        'PlateRow': {0: 'A', 1: 'A', 2: 'B', 3: 'B'},
        'PlateColumn': {0: '2', 1: '2', 2: '1', 3: '1'},
        'Frame': {0: 1, 1: 1, 2: 1, 3: 1},
        'Total': {0: 29.0, 1: 17.0, 2: 14.0, 3: 22.0},
        'Cell_percent': {0: 1.0, 1: 1.0, 2: 1.0, 3: 1.0}
    })

    frame = 1
    data = data_annotation.AnnotatedData(filepaths, frame)
    data.set_condition(
        condition='Foo', well_num=1, plate_num=1,
        plate_row='A', plate_column='2'
    )
    data.set_condition(
        condition='Bar', well_num=1, plate_num=2,
        plate_row='B', plate_column='1'
    )
    result = data.dataframe

    # We need to round off the floating point fields to test for equality
    result['Cell_percent'] = result['Cell_percent'].round(5)
    assert (result == target).all().all
    assert data.get_frame() == 1
