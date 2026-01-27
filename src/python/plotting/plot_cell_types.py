import os
import subprocess

#Creates a plot defined by cell typed using multiple BED file
# Assumes no thickStart, thickEnd, and block columns
def plot_by_cell_type(
    bed_files,
    region,
    output_file="celltype_plot.png",
    colormaps=["Reds", "Blues", "Greens", "coolwarm"], 
    #has to have the same number of colourmaps as BED files
    titles=None,
    trackLabelFraction=0.2,
    dpi=130,
    width=38,
    height=2,
    max_score=1000,
    min_score=0,
    temp_ini="temp.ini",
    gene_file=None
):

    if titles is None:
        titles = [os.path.basename(f).split(".")[0] for f in bed_files]

    with open(temp_ini, "w") as f:
        f.write("[x-axis]\nwhere = top\nshow_labels = false\n\n")
        f.write("[spacer]\nheight = 0.1\n\n")

        if gene_file:
            f.write(f"""
[{os.path.basename(gene_file).split(".")[0]}]
file = {gene_file}
file_type = bed
height = {height / 2}
title = gene:{os.path.basename(gene_file).split(".")[0]}
style = UCSC
color = green
border_color = black

[spacer]
height = 0.1

""")

        for i, bed in enumerate(bed_files):
            f.write(f"""
[{titles[i]}]
file = {bed}
file_type = bed
height = {height}
title = {titles[i]}
style = UCSC
color = {colormaps[i]}
border_color = black
arrow_interval = 10
fontsize = 10
show_labels = true
show_data_range = true
min_value = {min_score}
max_value = {max_score}
gene_rows = 3

[spacer]
height = 0.1

""")

    # Call pyGenomeTracks
    subprocess.run([
        "pyGenomeTracks",
        "--tracks", temp_ini,
        "--region", region,
        "--outFileName", output_file,
        "--dpi", str(dpi),
        "--width", str(width),
        "--trackLabelFraction", str(trackLabelFraction)
    ])

    print(f"✅ Plot saved to: {output_file}")
