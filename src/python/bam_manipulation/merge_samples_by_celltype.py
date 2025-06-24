from pathlib import Path

import pysam


def merge_samples_by_celltype(input_dir, output_dir, samples=["Mira_1", "Mira_2", "Mira_3", "Mira_4"]):
    celltypes = set()
    for sample in samples:
        p = Path(input_dir) / f"{sample}_files"
        for child in p.glob(f"{sample}_*.bam"):
            celltypes.add(child.name.split(sample + "_")[1].split(".bam")[0])

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for ct in celltypes:
        bam_files = Path(input_dir).glob(f"**/*{ct}*.bam")
        pysam.merge("-f", "-o", str(output_dir / f"{ct}.bam"), *[str(b) for b in bam_files])
