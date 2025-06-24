from pathlib import Path

from plotting.plot_cell_types import plot_by_cell_type
from plotting.plot_by_score import plot_by_score

TEMP_INI_PATH = Path() / "temp.ini"


def test_plot_by_cell_type_outputs():
    input_files = (Path(__file__).parent / "test_data").glob("volvox-bed12*.bed")
    output_file = Path() / "celltype_plot.png"
    output_file.unlink(missing_ok=True)
    plot_by_cell_type(
        #list the bed files:
        bed_files=input_files,
        #list the wanted region
        region="ctgA:1000-25000",
        output_file=output_file,
        #name the tissues denoted by BED files:
        titles=["Tissue1", "Tissue2", "Tissue3", "Tissue4"]
    )
    assert output_file.exists()
    output_file.unlink()
    TEMP_INI_PATH.unlink()


def test_plot_by_score_outputs():
    input_file = Path(__file__).parent / "test_data" / "volvox-bed12.bed"
    output_file = Path() / "plot_by_score.png"
    output_file.unlink(missing_ok=True)
    plot_by_score(
        bed_file=input_file,           
        region="ctgA:1000-23000",
        output_file=output_file,
    )
    assert output_file.exists()
    output_file.unlink()
    TEMP_INI_PATH.unlink()
