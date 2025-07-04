#!/usr/bin/env python
# coding: utf-8

# This is a script to rescale scores in a BED file (output from regtools) to 1000 per gene.
# Uses Python env 'venv', see scripts/Python_env_MARS.txt

# In[ ]:


import gffutils
import pandas as pd
import pyranges as pr
import matplotlib.pyplot as plt


# In[ ]:


# File paths
gff_file = "/mnt/data/project0061/ref/schistosoma_mansoni.PRJEA36577.WBPS19.annotations.gff3"
db_file = "annotations.db"
bed_file = "output.junctions.bed"


# In[ ]:


# Step 1: Create or load gffutils database
try:
    db = gffutils.FeatureDB(db_file)
    print("Loaded existing gffutils database.")
except Exception:
    print("Creating gffutils database, this may take a while...")
    db = gffutils.create_db(
        gff_file,
        dbfn=db_file,
        force=True,
        keep_order=True,
        merge_strategy="merge",
        sort_attribute_values=True,
    )
    print("Database created.")


# In[ ]:


# Step 2: Extract gene features into a DataFrame
genes = []
for gene in db.features_of_type("gene"):
    genes.append({
        "Chromosome": gene.chrom,
        "Start": gene.start - 1,  # Convert to 0-based for BED
        "End": gene.end,
        "Strand": gene.strand,
        "Gene": gene.id
    })

genes_df = pd.DataFrame(genes)
genes_pr = pr.PyRanges(genes_df)


# In[ ]:


# Step 3: Load your BED file into PyRanges
bed = pr.read_bed(bed_file)
bed_df = bed.df.copy()
bed_df["original_index"] = bed_df.index  # to track rows
bed = pr.PyRanges(bed_df)


# In[ ]:


# Step 4: Join BED with genes and count overlaps
joined = bed.join(genes_pr)
joined_df = joined.df

# Count unique gene overlaps per original BED entry
gene_counts = joined_df.groupby("original_index")["Gene"].nunique()

# Keep only those overlapping **exactly one** gene
keep_indices = gene_counts[gene_counts == 1].index

# Filter original join to those rows
filtered_df = joined_df[joined_df["original_index"].isin(keep_indices)]


# In[ ]:


# Step 5: Plot histogram of gene overlaps per original BED entry
plt.figure(figsize=(8, 5))
plt.hist(gene_counts, bins=range(1, gene_counts.max() + 2), color='steelblue', edgecolor='black', align='left')
plt.xlabel("Number of genes overlapped per BED entry")
plt.ylabel("Number of BED entries")
plt.title("Histogram of Gene Overlaps per BED Entry")
plt.xticks(range(1, gene_counts.max() + 1))
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig("bed_gene_overlap_histogram.png", dpi=300)
plt.show()


# In[ ]:


# Step 6: Rescale scores per gene
filtered_df = filtered_df.copy()
filtered_df.loc[:, "Score"] = pd.to_numeric(filtered_df["Score"], errors="coerce").fillna(0)

def scale_scores(group):
    scores = group["Score"].astype(float)
    total = scores.sum()
    if total == 0:
        group["Score"] = 0.0
    else:
        scaled = (scores / total) * 1000
        group["Score"] = scaled.round(2)
    return group

# Apply the scaling function per gene
scaled_df = (
    filtered_df
    .copy()
    .groupby("Gene", group_keys=False)
    .apply(scale_scores)
)

# Round and convert scores to integer
scaled_df["Score"] = scaled_df["Score"].round(2).astype(int)


# In[ ]:


# Step 7: Map scaled scores back to original BED rows
original_bed = bed.df.set_index("original_index")
scaled_df = scaled_df.set_index("original_index")
original_bed["Score"] = original_bed["Score"].astype(float)
original_bed.loc[scaled_df.index, "Score"] = scaled_df["Score"]

# Clean up
output_df = original_bed.reset_index(drop=True)


# In[ ]:


# Step 8: Save to BED file
bed_cols = [col for col in output_df.columns if col not in ["Gene"]]
output_df[bed_cols].to_csv("scaled_output.filtered.bed", sep="\t", header=False, index=False)

