# pylint: disable=redefined-outer-name
from pathlib import Path

import pytest

from bam_manipulation.wp3_add_ic_tag import main as add_ic_tag


@pytest.fixture
def small_bam():
    return Path(__file__).parent / "test_data" / "possorted_genome_bam.sample.CB.bam"


def test_add_ic_tag_without_cluster_map(small_bam):
    output_file = Path() / "test.bam"
    output_file_index = Path() / "test.bam.bai"
    output_file.unlink(missing_ok=True)
    add_ic_tag(["-i", str(small_bam), "-o", str(output_file)])
    assert output_file.exists()
    output_file.unlink()
    output_file_index.unlink()
