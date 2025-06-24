import os
import subprocess

#Creates a plot defined by score from a single BED file
# Assumes no thickStart, thickEnd, and block columns
def plot_by_score(
    bed_file,
    region,
    output_file="plot_by_score.png",
    height=2,
    title="test",
    colour="coolwarm", #change the colorscheme as desired
    trackLabelFraction=0.2,
    dpi=130,
    width=38,
    temp_ini="temp.ini"
):
    with open(temp_ini, "w") as f:
        f.write(f"""
[x-axis]
where = top
show_labels = false

[spacer]
height = 0.05

[score shading]
height = {height}
title = {title}
style = UCSC
border_color = black
arrow_interval = 10
fontsize = 10
file = {bed_file}
show_labels = true
show_data_range = true
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
