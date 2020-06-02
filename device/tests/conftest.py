import pytest
from path import Path


@pytest.fixture()
def raw_hub_data():
    test_dir = Path(__file__).parent
    hub_data_file = test_dir / 'raw_hub_data.json'
    return hub_data_file.read_text()
