import plate


def test_get_tag_info():
    p = plate.Plate()
    tags = ["foobar", "well_num=3", "plate_num=2"]
    assert p._get_tag_info(tags, "well_num=") == 3
    assert p._get_tag_info(tags, "plate_num=") == 2
