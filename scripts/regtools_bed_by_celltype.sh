#This is a script to run regtools for each bam file in a directory, extract junctions,
#and edit the bed file resulting from each bam to assign a custom rgb code, and concatenate the resulting bed files together.

$BAM_DIR=$1 #Directory containing BAM files split by cell type. Cell type is the first part of the filename before an underscore.
$OUTPUT_BED_DIR=$2 #Directory to output the resulting bed files.

$REGTOOLS_DIR=$3 #Directory containing regtools executable.
$REGTOOLS=$REGTOOLS_DIR/regtools   

#Make output directory if it doesn't exist
mkdir -p $OUTPUT_BED_DIR
#Loop through each BAM file in the directory
for BAM_FILE in $BAM_DIR/*.bam; do
    #Extract the cell type from the filename
    CELL_TYPE=$(basename "$BAM_FILE" | cut -d'_' -f1) #Assuming cell type is the first part of the filename before an underscore
    #Define the output bed file name
    OUTPUT_BED_FILE="$OUTPUT_BED_DIR/${CELL_TYPE}_junctions.bed"
    #Run regtools to extract junctions
    $REGTOOLS junctions extract "$BAM_FILE" -s XS -o "$OUTPUT_BED_FILE"
    #Count the number of bam files in the directory
    BAM_COUNT=$(ls $BAM_DIR/*.bam | wc -l)
    #Generate a custom RGB code (for example, red) for each cell type
    

    #Check if the output bed file was created successfully
    if [ -f "$OUTPUT_BED_FILE" ]; then
        #Add custom RGB code to the bed file
        awk -v rgb="255,0,0" 'BEGIN{OFS="\t"} {print $0, rgb}' "$OUTPUT_BED_FILE" > "${OUTPUT_BED_FILE%.bed}_rgb.bed"
        #Rename the file to the original name with RGB added
        mv "${OUTPUT_BED_FILE%.bed}_rgb.bed" "$OUTPUT_BED_FILE"
        echo "Processed $BAM_FILE -> $OUTPUT_BED_FILE with RGB code $rgb"
    else
        echo "Failed to create output bed file for $BAM_FILE"
    fi
done
