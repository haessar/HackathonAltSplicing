from pathlib import Path

from plotting.plot_cell_types import plot_by_cell_type


if __name__ == "__main__":
    TEMP_INI_PATH = Path() / "temp.ini"
    input_files = (Path(__file__).parent / "plot_inputs").glob("*.filtered.bed")
    gene_file = (Path(__file__).parent / "plot_inputs" / "Smp_028030.1.CDS.bed")
    output_file = Path(__file__).parent / "celltype_plot_with_gene.png"
    output_file.unlink(missing_ok=True)
    plot_by_cell_type(
        bed_files=sorted(input_files),
        region="SM_V10_1:48480000-48500000",
        output_file=output_file,
        titles=["Muscle_1", "Muscle_2", "Stem_B", "Stem_C"],
        colormaps=["Reds", "Reds", "Blues", "Blues"],
        max_score=100,
        min_score=10,
        gene_file=gene_file,
        height=3
    )
    TEMP_INI_PATH.unlink()
