<!-- vim-markdown-toc GFM -->

* [Outline](#outline)
* [Setup](#setup)
* [Run](#run)

<!-- vim-markdown-toc -->

# Outline

We want to assign reads to existing or novel isoforms so that later we can
group and visualize reads supporting an isoform.

Starting from a reference genome and paired fastq. Steps:

* Align reads to reference using hisat2 (not done as I already have an aligned bam)

* Use [stringtie](https://github.com/gpertea/stringtie) to assemble
  transcripts. We give stringtie the reference annotation to guide the assembly.

* Extract fasta file for each transcript

* Use [kallisto v0.48](https://pachterlab.github.io/kallisto/manual.html) to map reads to the assembled transcripts

# Setup

```
conda create -n HackathonAltSplicing
conda activate HackathonAltSplicing
conda install --file requirements.txt --yes
```

# Run

```
snakemake -n -p -j 10 -C \
    bam=data/ERR11178264_Illumina_NovaSeq_6000_paired_end_sequencing.bam \
    genome=data/schistosoma_mansoni.PRJEA36577.WBPS19.genomic_softmasked.fa \
    gff=ref/schistosoma_mansoni.PRJEA36577.WBPS19.canonical_geneset.gtf \
    -d /export/projects/III-data/wcmp_bioinformatics/db291g/projects/20250604_HackathonAltSplicing \
    --use-conda
```


