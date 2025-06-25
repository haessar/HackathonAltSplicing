#!/usr/bin/env bash
#SBATCH --account=project0061
#SBATCH --job-name=smk_mansoni
#SBATCH --output=logs/smk_%A_%a.out        # one log per array task
#SBATCH --error=logs/smk_%A_%a.err
#SBATCH --time=02:00:00                    # adjust
#SBATCH --cpus-per-task=12                 # threads available to Snakemake
#SBATCH --mem=16G                          # adjust
#SBATCH --partition=nodes                # adjust or delete if default
#SBATCH --nodes=1
#SBATCH --array=0-16

#
# ── ARRAY ────────────────────────────────────────────────────────────────
# Submit with, e.g.:
#   sbatch --array=0-$(($(ls all_samples_bams/*.bam | wc -l)-1)) run_snakemake_array.sh
# or hard-code the range:  #SBATCH --array=0-143  (for 144 .bam files)
# ─────────────────────────────────────────────────────────────────────────

set -euo pipefail

# 1. Pick the BAM that corresponds to this array index
BAM_DIR="/mnt/data/project0061/will/all_samples_bams"
mapfile -t BAM_LIST < <(ls -1 "${BAM_DIR}"/*.bam)
BAM_FILE="${BAM_LIST[$SLURM_ARRAY_TASK_ID]}"
SAMPLE_ID="$(basename "${BAM_FILE}" .bam)"

# 2. (Optional) load software environment
source ~/miniconda3/etc/profile.d/conda.sh
conda activate HackathonAltSplicing

# 3. Run Snakemake (within HackathonAltSplicing/isoform_detection/) for this sample
snakemake -p \
          -j 10 \
	  --profile profile/ \
          -C sample_id="${SAMPLE_ID}" \
             bam="${BAM_FILE}" \
             genome="../bam_manipulation/published/Smansoni_genome/fasta/genome.fa" \
             gff="../ref/schistosoma_mansoni.PRJEA36577.WBPS19.annotations.gff3" \
             read_mode=single \
             fragment_length=300 \
             fragment_sd=100 \
          --latency-wait 60 \
          -d /mnt/data/project0061/will \
          --use-conda \
          --cores "${SLURM_CPUS_PER_TASK}"


