import pytest
import pandas as pd
from tablespy.inspector import Inspector

BLANK_COLS = 500
BLANK_ROWS = 500


@pytest.fixture
def blank_data():
    return [
        [''] * BLANK_COLS
    ] * BLANK_ROWS

@pytest.fixture
def basic_df(blank_data):
    df = pd.DataFrame(blank_data)
    df.iloc[3, 11] = "Test Title"
    df.iloc[4:50, 11] = range(1, 47)
    df.iloc[4:50, 12] = 12
    df.iloc[4:50, 13:20] = 'A'
    return df

@pytest.fixture
def double_df(basic_df):
    df = basic_df.copy()
    df.iloc[213, 11] = "Other"
    df.iloc[213, 12] = "Title"
    df.iloc[214:250, 11] = range(1, 37)
    df.iloc[214:250, 12] = 12
    df.iloc[220:250, 12] = ''
    df.iloc[214:250, 13:20] = 'A'
    df.iloc[214:250, 18] = ''

    # This leaves a single column isolated - too narrow to count as a table, hence double_df,
    # not triple

    return df

class TestInspector:
    def test_can_extract_simple_table(self, basic_df):
        inspector = Inspector()
        inspection = inspector.inspect_df(basic_df)

        assert list(inspection.regions.keys()) == [1]
        assert inspection.regions[1]['lower-left'] == (4, 11)
        assert inspection.regions[1]['upper-right'] == (49, 19)
        assert inspection.regions[1]['header-boundary'] == (4, 19)
        assert inspection.regions[1]['title']['loc'] == (3, 11, 1)
        assert inspection.regions[1]['title']['text'] == "Test Title"

    def test_can_extract_double_table(self, double_df):
        inspector = Inspector()
        inspection = inspector.inspect_df(double_df)

        assert list(inspection.regions.keys()) == [1, 2]

        first_key = [i for i, v in inspection.regions.items() if v['title']['text'] == 'Test Title'][0]
        second_key = 3 - first_key

        assert inspection.regions[first_key]['lower-left'] == (4, 11)
        assert inspection.regions[first_key]['upper-right'] == (49, 19)
        assert inspection.regions[first_key]['header-boundary'] == (4, 19)
        assert inspection.regions[first_key]['title']['loc'] == (3, 11, 1)
        assert inspection.regions[first_key]['title']['text'] == "Test Title"

        assert inspection.regions[second_key]['lower-left'] == (214, 11)
        assert inspection.regions[second_key]['upper-right'] == (249, 17)
        assert inspection.regions[second_key]['header-boundary'] == (214, 17)
        assert inspection.regions[second_key]['title']['loc'] == (213, 11, 2)
        assert inspection.regions[second_key]['title']['text'] == "Other\nTitle"
