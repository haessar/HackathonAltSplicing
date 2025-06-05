import os
import subprocess

def plot_exon_intron(
    bed_file,
    region,
    output_file="intron_exon_plot.png",
    height=2,
    title="test",
    temp_ini="temp.ini",
    use_itemRGB=False
):
    with open(temp_ini, "w") as f:
        f.write(f"""
[x-axis]
where = top
show_labels = false

[spacer]
height = 0.05
""")

        if use_itemRGB:
            f.write(f"""
[itemRGB shading]
height = {height}
title = {title}
style = exonarrows
border_color = black
arrow_interval = 10
fontsize = 10
file = {bed_file}
show_labels = true
show_data_range = false
use_itemRGB = true
""")
        else:
            f.write(f"""
[score shading]
height = {height}
title = {title}
style = exonarrows
border_color = black
arrow_interval = 10
fontsize = 10
color = Reds
file = {bed_file}
show_labels = true
show_data_range = true
""")

    # Call pyGenomeTracks
    subprocess.run([
        "pyGenomeTracks",
        "--tracks", temp_ini,
        "--region", region,
        "--outFileName", output_file
    ])

    print(f"✅ Plot saved to: {output_file}")


# Example call
plot_exon_intron(
    bed_file="volvox-bed12.bed",           
    region="ctgA:1000-23000",
    output_file="intron_exon_plot.png",
    use_itemRGB=False #change whether the colour is by score or itemRGB
)
