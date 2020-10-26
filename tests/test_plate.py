from fucci_analysis import plate


def test_get_tag_info():
    p = plate.Plate()
    tags = ["foobar", "well_num=3", "plate_num=2"]
    assert p.get_tag_info(tags, "well_num=") == 3
    assert p.get_tag_info(tags, "plate_num=") == 2

def test_xy_to_well_num():
    p = plate.Plate()
    assert p.xy_to_well_num(4, 3) == 41
    for x in range(plate.X_DIMENSION_WELLS):
        for y in range(plate.Y_DIMENSION_WELLS):
            assert p.well_num_to_xy(p.xy_to_well_num(x,y)) == (x,y)

def test_well_num_to_xy():
    p = plate.Plate()
    assert p.well_num_to_xy(15) == (2, 1)
    for well_num in range(1, plate.WELL_COUNT + 1):
        assert p.xy_to_well_num(*p.well_num_to_xy(well_num)) == well_num
