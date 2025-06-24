import pysam
import pandas as pd
import os
from multiprocessing import Pool, Lock

# Output file path for saving results
output_file = "barcode_coverage_parallel_results.csv"
lock = Lock()

# Load the list of barcodes from the input CSV
barcode_df = pd.read_csv("/mnt/data/project0061/bam_manipulation/published/cc_barcode.csv")
barcodes = set(barcode_df['cell_barcode'])

# Define the base path to all sample directories
base_path = "/mnt/data/project0061/bam_manipulation/published/cellranger_count_Sm"
samples = ["Mira_1", "Mira_2", "Mira_3", "Mira_4"]

def process_sample(sample):
    bam_path = os.path.join(base_path, sample, "outs", "possorted_genome_bam.bam")
    print(f"Processing sample: {sample} ({bam_path})")

    if not os.path.exists(bam_path):
        print(f"BAM file not found for sample: {sample}")
        return None

    bam = pysam.AlignmentFile(bam_path, "rb")
    total_reads = 0
    matched_reads = 0

    for read in bam.fetch(until_eof=True):
        total_reads += 1
        tags = dict(read.get_tags())
        if "CB" in tags and tags["CB"] in barcodes:
            matched_reads += 1

        if total_reads % 5_000_000 == 0:
            print(f"{sample}: {total_reads:,} reads processed")

    bam.close()

    coverage_pct = (matched_reads / total_reads * 100) if total_reads > 0 else 0

    result = {
        "Sample": sample,
        "Total Reads": total_reads,
        "Matched Barcodes": matched_reads,
        "Coverage (%)": round(coverage_pct, 2)
    }

    # Save the result immediately after processing each sample
    with lock:
        df = pd.DataFrame([result])
        if not os.path.exists(output_file):
            df.to_csv(output_file, index=False)
        else:
            df.to_csv(output_file, mode='a', header=False, index=False)
        print(f"Finished processing {sample}. Results written to file.")

    return result

if __name__ == "__main__":
    with Pool(processes=4) as pool:
        pool.map(process_sample, samples)

    print(f"All samples have been processed. Results saved to {output_file}")