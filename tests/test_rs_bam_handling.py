# pylint: disable=redefined-outer-name
from pathlib import Path
import shutil

import pytest

from bam_manipulation.rs_bam_handling import bamTagHandling


@pytest.fixture
def small_bam():
    return Path(__file__).parent / "test_data" / "possorted_genome_bam.sample.CB.bam"


@pytest.fixture
def mapping_tsv():
    return Path(__file__).parent / "test_data" / "cell_barcodes_labeled.tsv"


def test_mapped_files_created(small_bam, mapping_tsv):
    expected_output_dir = Path() / "possorted_genome_bam.sample.CB_tag_files"
    expected_files = {"Muscle.bam", "Stem_A.bam", "Stem_B.bam", "untagged.bam"}
    shutil.rmtree(expected_output_dir, ignore_errors=True)
    bamTagHandling(str(small_bam), mapping=str(mapping_tsv), delim="\t")
    assert expected_output_dir.exists()
    assert set(p.name for p in expected_output_dir.iterdir()) == expected_files
    shutil.rmtree(expected_output_dir, ignore_errors=True)
