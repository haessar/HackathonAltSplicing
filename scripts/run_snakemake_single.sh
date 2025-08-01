#!/usr/bin/env bash
#SBATCH --account=project0061
#SBATCH --job-name=smk_mansoni
#SBATCH --output=logs/smk_%A_%a.out        # one log per array task
#SBATCH --error=logs/smk_%A_%a.err
#SBATCH --time=12:00:00                    # adjust
#SBATCH --cpus-per-task=128                 # threads available to Snakemake
#SBATCH --mem=64G                          # adjust
#SBATCH --partition=nodes                # adjust or delete if default
#SBATCH --nodes=1

#
# ── ARRAY ────────────────────────────────────────────────────────────────
# Submit with:
#   sbatch run_snakemake_single.sh
# ─────────────────────────────────────────────────────────────────────────

set -euo pipefail

# 1. Pick the BAM that corresponds to this array index
BAM_FILE="/mnt/data/project0061/will/Sm_female_ROI_bam/female_ROI.sam.bam.sort"
SAMPLE_ID="Sm_female_ROI"

# 2. (Optional) load software environment
source ~/miniconda3/etc/profile.d/conda.sh
conda activate HackathonAltSplicing

# 3. Run Snakemake (within HackathonAltSplicing/isoform_detection/) for this sample
snakemake -p \
          -j 10 \
	  --profile profile/ \
          -C sample_id="${SAMPLE_ID}" \
             bam="${BAM_FILE}" \
             genome="../bam_manipulation/published/Smansoni_genome/fasta/SM_V9_ENA.fa" \
             gff="../ref/SM_V9_ENA.gff" \
             read_mode=single \
             fragment_length=300 \
             fragment_sd=100 \
          --latency-wait 60 \
          -d /mnt/data/project0061/will \
          --use-conda \
          --cores "${SLURM_CPUS_PER_TASK}"


