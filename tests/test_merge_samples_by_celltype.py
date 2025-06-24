from pathlib import Path
import shutil

from bam_manipulation.merge_samples_by_celltype import merge_samples_by_celltype

def test_merge_samples_by_celltype():
    input_dir = Path(__file__).parent / "test_data" / "dummy_bams"
    output_dir = Path() / "test_merged"
    expected_files = {"Neuron_1.bam", "Stem_C.bam", "Stem_D.bam", "Muscle_1.bam"}
    shutil.rmtree(output_dir, ignore_errors=True)
    merge_samples_by_celltype(input_dir, output_dir)
    assert output_dir.exists()
    assert set(f.name for f in output_dir.iterdir()) == expected_files
    shutil.rmtree(output_dir, ignore_errors=True)
