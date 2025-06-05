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
    temp_ini="temp.ini"
):

    if titles is None:
        titles = [os.path.basename(f).split(".")[0] for f in bed_files]

    with open(temp_ini, "w") as f:
        f.write("[x-axis]\nwhere = top\nshow_labels = false\n\n")
        f.write("[spacer]\nheight = 0.1\n\n")

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

[spacer]
height = 0.5

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


plot_by_cell_type(
    #list the bed files:
    bed_files=["volvox-bed12.bed","volvox-bed12_1.bed", "volvox-bed12_2.bed", "volvox-bed12_3.bed"],     
    #list the wanted region
    region="ctgA:1000-25000",
    output_file="celltype_plot.png",
    #name the tissues denoted by BED files:
    titles=["Tissue1", "Tissue2", "Tissue3", "Tissue4"]
)
