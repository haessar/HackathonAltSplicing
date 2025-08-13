from collections import Counter
import pysam
import pandas as pd
import os
from multiprocessing import get_context, Lock

# Output file path for saving results
output_file = "barcode_coverage_parallel_results.csv"
lock = Lock()

# Load barcodes CSV once globally
barcode_df = pd.read_csv("/mnt/data/project0061/bam_manipulation/published/cc_barcode.csv")

# Sample name mapping
sample_map = {
    "Mira_1": "sample1",
    "Mira_3": "sample2",
    "Mira_4": "sample3",
    "Mira_2": "sample4"
}

# BAM base path and sample list
base_path = "/mnt/data/project0061/bam_manipulation/published/cellranger_count_Sm"
samples = ["Mira_1", "Mira_2", "Mira_3", "Mira_4"]

def process_sample(sample):
    bam_path = os.path.join(base_path, sample, "outs", "possorted_genome_bam.bam")
    print(f"Processing sample: {sample} ({bam_path})")

    if not os.path.exists(bam_path):
        print(f"❌ BAM file not found for {sample}")
        return None

    csv_sample_name = sample_map[sample]
    barcodes = set(barcode_df[barcode_df["sample"] == csv_sample_name]["cell_barcode"])

    total_reads = 0
    matched_reads = 0
    elsewhere_reads = []

    with pysam.AlignmentFile(bam_path, "rb") as bam:
        for read in bam.fetch(until_eof=True):
            total_reads += 1
            tags = dict(read.get_tags())
            if "CB" in tags and tags["CB"] in barcodes:
                matched_reads += 1
            elif "CB" in tags and tags["CB"] in set(barcode_df['cell_barcode']):
                elsewhere_reads.append(barcode_df[barcode_df["cell_barcode"] == tags["CB"]]["sample"].values[0])
            if total_reads % 5_000_000 == 0:
                print(f"{sample}: {total_reads:,} reads processed")

    coverage_pct = (matched_reads / total_reads * 100) if total_reads > 0 else 0

    result = {
        "Sample": sample,
        "Total Reads": total_reads,
        "Matched Barcodes": matched_reads,
        "Coverage (%)": round(coverage_pct, 2)
    }

    print(f"{sample} reads from elsewhere: {Counter(elsewhere_reads)}")

    # Save result (thread-safe)
    with lock:
        df = pd.DataFrame([result])
        write_mode = 'a' if os.path.exists(output_file) else 'w'
        header = not os.path.exists(output_file)
        df.to_csv(output_file, mode=write_mode, index=False, header=header)
        print(f"✅ Finished {sample}. Results written.")

    return result

if __name__ == "__main__":
    # Multiprocessing with spawn method (safe in Conda envs)
    with get_context("spawn").Pool(processes=4) as pool:
        pool.map(process_sample, samples)

    print(f"✅ All samples processed. Results saved to {output_file}")
