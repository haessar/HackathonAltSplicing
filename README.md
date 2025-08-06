# HackathonAltSplicing

![image](https://github.com/user-attachments/assets/3f94eb52-b412-4ec2-96fc-67f5e3fb34d3)

## Quick Start

Clone the repository and change directory:

```
git clone https://github.com/haessar/HackathonAltSplicing.git
cd HackathonAltSplicing
```

For running Python scripts or notebooks in `scripts` directory, first setup a Python virtual environment (tested with v3.10) and install package dependencies:

```
python3 -m venv venv-name
source venv-name/bin/activate
pip install .
python3 scripts/script_name.py [args]
```

### Isoform detection pipeline

For running the snakemake pipeline in the `isoform_detection` directory (corresponding to Workflow 2 in figure above), install conda (e.g. [Miniforge download link](https://conda-forge.org/download/)) and follow the guide in `docs/isoform_detection.md`. Slurm bash scripts for running on a HPC system can be found in the `scripts` directory.

### JBrowse 2 with plugin and custom tracks

For running JBrowse 2 with the plugin developed for Workflow 1, ensure Node.js is installed (e.g. `sudo apt install nodejs npm`) and follow the guide in `jbrowse-plugin-bedfeaturecoloring/README.md`. To serve a custom `config.json` for loading in tracks for analysis, in a new terminal:

```
cd analysis/jbrowse_env/
npx serve . --cors -p 3001
```

and navigate to `http://localhost:3000/?config=http://localhost:3001/config.json` in a web browser.

## Contributing

### 🔖 Issue Labelling

I've created issues that reflect the work packages that I outlined in the introductory slides (for some of them it made sense to split them in two). Work package #1 is signified by `(WP1)`, etc. I've used labels to designate which "theme" they belong to, whether they have a significant MARS component, and whether they are `Coding` or `Research` heavy. When determining what you want to work on, you can filter the labels that appeal to you or are a suitable match to your skillset (e.g. if you have no interest in using MARS, you could filter out the `MARS` label).

### 🔀 Branching Strategy

As there will be lots of us working feverishly in the same repo, I recommend we use **feature branches** for all development work rather than `main`.  

- Create a new branch from `main` for each new feature or fix (perhaps to work on a GitHub issue):  
  ```bash
  git checkout -b your-feature-name
  ```
- Once you're happy with changes, open a pull request to merge into `main` and someone can review them.

- This will help prevent conflicts, support collaboration, and maintain a clean commit history.
