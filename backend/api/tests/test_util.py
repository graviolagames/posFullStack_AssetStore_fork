import pytest
from util import data_util 

# Test string-to hash generation
def test_create_hash():
    # Should generate a predictable hash
    input_string = "Hello, World!"
    expected_hash = "65a8e27d8879283831b664bd8b7f0ad4"
    assert data_util.create_hash(input_string) == expected_hash

    # Should return the correct value for an empty string
    input_string = ""
    expected_hash = "d41d8cd98f00b204e9800998ecf8427e"
    assert data_util.create_hash(input_string) == expected_hash
