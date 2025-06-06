#!/usr/bin/env python
# coding: utf-8

# This is a script to run regtools for each bam file in a directory, extract junctions, and edit the resulting bed files to assign a custom rgb code corresponding to cell type. The resulting bed files are then concatenated together.
# 
# Uses Python env 'venv', see scripts/Python_env_MARS.txt

# In[1]:


import os
import colorsys
import pysam
import pysam.samtools


# In[ ]:


# Loop through BAM files in a directory and extract cell types
#Assuming BAM files are named like "celltype_sample.bam"
BAM_DIR = os.environ.get('BAM_DIR', '/mnt/data/project0061/frances/bam_dir')
bam_files = [f for f in os.listdir(BAM_DIR) if f.endswith('.bam')]
celltypes = [f.split('_')[2] for f in bam_files] #Celltype not currently consistent- sometimes multiple '_' in name
print(celltypes)


# In[ ]:


# Generate a unique RGB color for each celltype
num_celltypes = len(celltypes)
colors = [colorsys.hsv_to_rgb(i / num_celltypes, 0.7, 0.9) for i in range(num_celltypes)]
rgb_colors = [(int(r * 255), int(g * 255), int(b * 255)) for r, g, b in colors]
celltype_colors = dict(zip(celltypes, rgb_colors))
print(celltype_colors)


# In[ ]:


# Run regtools to generate BED files with splice junctions for each BAM file
for bam_file in bam_files:
    celltype = bam_file.split('_')[2]
    bam_path = os.path.join(BAM_DIR, bam_file)
    bed_file = os.path.splitext(bam_file)[0] + ".junctions.bed"
    bed_path = os.path.join(BAM_DIR, bed_file)
    # Run regtools junctions extract
    os.system(f"/mnt/data/project0061/frances/regtools/build/regtools junctions extract -s XS {bam_path} -o {bed_path}")


# In[ ]:


# Edit column 8 of each BED file to have the specific RGB code for the celltype and append .rgb to the bed file name
for bam_file in bam_files:
    celltype = bam_file.split('_')[2]
    rgb = ','.join(map(str, celltype_colors.get(celltype, (0, 0, 0))))  # Default to black if not found
    bed_file = os.path.splitext(bam_file)[0] + ".junctions.bed"
    if not os.path.exists(bed_path):
        continue
    bed_path = os.path.join(BAM_DIR, bed_file)
    rgb_bed_file = bed_file + ".rgb"
    rgb_bed_path = os.path.join(BAM_DIR, rgb_bed_file)
    with open(bed_path, 'r') as infile, open(rgb_bed_path, 'w') as outfile:
        for line in infile:
            fields = line.rstrip('\n').split('\t')
            # BED format: add RGB as 9th column (index 8), fill missing columns with '.'
            while len(fields) < 9:
                fields.append('.')
            fields[8] = rgb
            outfile.write('\t'.join(fields) + '\n')


# In[ ]:


# Concatenate all .junctions.bed.rgb files into a single file
rgb_bed_files = [os.path.join(BAM_DIR, os.path.splitext(f)[0] + ".junctions.bed.rgb") for f in bam_files]
concatenated_bed_path = os.path.join(BAM_DIR, "all_celltypes.junctions.bed.rgb")

with open(concatenated_bed_path, 'w') as outfile:
    for rgb_bed_file in rgb_bed_files:
        with open(rgb_bed_file, 'r') as infile:
            for line in infile:
                outfile.write(line)
print(f"Concatenated BED file created at: {concatenated_bed_path}")

