#!/bin/bash -l

##Run this script on MARS to map single cell data to the S. mansoni genome (v10) using Cellranger (v9.0.0)
##NB make sure you have added cellranger v9 to your PATH before running
#export PATH=/mnt/data/project0014/Frances/Atlas_review/Cellranger/cellranger-9.0.0/:$PATH
##Run the script like this (changing resources as required, depending on data):
#sbatch --cpus-per-task=12 --mem=34G /mnt/data/project0014/Frances/Atlas_review/Scripts/cr_count_miracidia.sh

##Make a dir containing the fastq files you want to map and then specify the path to this dir using the variable "FASTQ_DIR" below
##Make sure you have renamed your fastq files as specified in the Cellranger documentation e.g. MySample_S1_L001_R1_001.fastq.gz
##Each set of paired fastq reads needs to be in a directory named after the sample. e.g. for sample 41427_4_4:
#/mnt/data/project0014/SC_data/to_map/41427_4_4/41427_4_4_S1_L001_R1_001.fastq.gz #(and R2 in the same dir)
##I do this by creating symlinks in the dir to_map to the original fastq file directories in SC_data e.g.
#ln -s /mnt/data/project0014/SC_data/Miracidia_Tess/Mira_1 /mnt/data/project0014/SC_data/to_map/
#ln -s /mnt/data/project0014/SC_data/Miracidia_Tess/Mira_2 /mnt/data/project0014/SC_data/to_map/
#ln -s /mnt/data/project0014/SC_data/Miracidia_Tess/Mira_3 /mnt/data/project0014/SC_data/to_map/
#ln -s /mnt/data/project0014/SC_data/Miracidia_Tess/Mira_4 /mnt/data/project0014/SC_data/to_map/
#ln -s /mnt/data/project0014/SC_data/Somules_Carmen/Som_2 /mnt/data/project0014/SC_data/to_map/
#ln -s /mnt/data/project0014/SC_data/Somules_Carmen/Som_3 /mnt/data/project0014/SC_data/to_map/

############# SLURM SETTINGS #############
#SBATCH --account=project0061   # account name (mandatory), if the job runs under a project then it'll be the project name, if not then it should =none
#SBATCH --job-name=alignment        # some descriptive job name of your choice
#SBATCH --output=%x-%j.out      # output file name will contain job name + job ID
#SBATCH --error=%x-%j.err       # error file name will contain job name + job ID
#SBATCH --partition=nodes        # which partition to use, default on MARS is “nodes"
#SBATCH --time=0-20:00:00       # time limit for the whole run, in the form of d-hh:mm:ss, also accepts mm, mm:ss, hh:mm:ss, d-hh, d-hh:mm
#SBATCH --mem=34G                # memory required per node, in the form of [num][M|G|T]
#SBATCH --nodes=1               # number of nodes to allocate, default is 1
#SBATCH --cpus-per-task=12       # number of processor cores to be assigned for each task, default is 1, increase for multi-threaded runs
#SBATCH --mail-user r.arif.1@research.gla.ac.uk     
#SBATCH --mail-type BEGIN,END
############# LOADING MODULES (optional) #############
module load apps/apptainer
############# CODE ############

#Define reference transcriptome
##S. mansoni # spell-checker: disable-line
REFERENCE="/mnt/autofs/data/userdata/project0061/bam_manipulation/published/Smansoni_genome" # spell-checker: disable-line

#Define output directory
OUTPUT_DIR="/mnt/autofs/data/userdata/project0061/bam_manipulation/published/cellranger_count_Sm" # spell-checker: disable-line

#Define dir containing fastq files - NB I usually create a symlink to the original fastq files in to_map to save moving/editing raw fastq files # spell-checker: disable-line
FASTQ_DIR="/mnt/autofs/data/userdata/project0061/bam_manipulation/published/reads" # spell-checker: disable-line

#Ensure the output directory exists
mkdir -p "$OUTPUT_DIR"

#Loop through each sample directory in the FASTQ directory --> remember that the fastq files need to be in a directory named after the sample!! # spell-checker: disable-line
for sample_dir in "$FASTQ_DIR"/*; do
    # Ensure the item is a directory
    if [ -d "$sample_dir" ]; then
        sample_id=$(basename "$sample_dir")
        echo "Processing sample: $sample_id"
        echo "$sample_dir"
        #Run cellranger count S. mansoni ref
        /mnt/data/project0061/bin/cellranger_v6.1.1 count --id="$sample_id"  --transcriptome="$REFERENCE" --sample="$sample_id" --fastqs="$sample_dir"  # spell-checker: disable-line

        #Check if cellranger count was successful # spell-checker: disable-line
        if [ $? -eq 0 ]; then
            echo "Sample $sample_id processed successfully."
            # Move the output to the desired directory
            mv "$sample_id" "$OUTPUT_DIR/$sample_id"
        else
            echo "Error processing sample $sample_id" >&2
        fi
    fi      
done
