import pysam
import pandas as pd
import os

# Load barcodes
barcode_df = pd.read_csv("/mnt/data/project0061/bam_manipulation/published/cc_barcode.csv")

# Sample name mapping from CSV to BAM folder names
sample_map = {
    "Mira_1": "sample1",
    "Mira_3": "sample2",
    "Mira_4": "sample3",
    "Mira_2": "sample4"
}

# Define BAM file paths
base_path = "/mnt/data/project0061/bam_manipulation/published/cellranger_count_Sm"
samples = ["Mira_1", "Mira_2", "Mira_3", "Mira_4"]

results = []

for sample in samples:
    bam_path = os.path.join(base_path, sample, "outs", "possorted_genome_bam.bam")
    if not os.path.exists(bam_path):
        print(f"BAM file not found: {bam_path}")
        continue

    # Get only barcodes for the current sample (from CSV)
    csv_sample_name = sample_map[sample]
    barcodes = set(barcode_df[barcode_df['sample'] == csv_sample_name]['cell_barcode'])

    print(f"Processing {sample} with {len(barcodes)} barcodes...")
    bam = pysam.AlignmentFile(bam_path, "rb")

    total_reads = 0
    matched_reads = 0

    for read in bam.fetch(until_eof=True):
        total_reads += 1
        tags = dict(read.get_tags())
        if "CB" in tags and tags["CB"] in barcodes:
            matched_reads += 1

    bam.close()

    coverage_pct = (matched_reads / total_reads) * 100 if total_reads > 0 else 0

    results.append({
        "Sample": sample,
        "Total Reads": total_reads,
        "Matched Barcodes": matched_reads,
        "Coverage (%)": round(coverage_pct, 2)
    })

# Save result
df_result = pd.DataFrame(results)
df_result.to_csv("barcode_coverage_summary.csv", index=False)
print(df_result)
