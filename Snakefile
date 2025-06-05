sample_id = os.path.basename(re.sub("\.bam", "", config["bam"]))


rule all:
    input:
        expand("kallisto/{sample_id}/read_transcripts.tsv.gz", sample_id=sample_id),


rule stringtie:
    input:
        bam="data/{sample_id}.bam",
        gff="ref/schistosoma_mansoni.PRJEA36577.WBPS19.annotations.gff3",
    output:
        gtf="stringtie/{sample_id}.gtf",
    shell:
        r"""
        stringtie -o {output.gtf} \
            -p 24 \
            -G {input.gff} \ 
            {input.bam} 
        """


rule fastaForTranscripts:
    input:
        gtf="stringtie/{sample_id}.gtf",
        genome="ref/schistosoma_mansoni.PRJEA36577.WBPS19.genomic_softmasked.fa",
    output:
        fa="stringtie/{sample_id}.fa",
    shell:
        r"""
        gffread -w {output.fa} \
            -g {input.genome} \
            {input.gtf}
        """


rule kallisto_index:
    input:
        fa="stringtie/{sample_id}.fa",
    output:
        idx="kallisto/{sample_id}.idx",
    conda:
        "env/kallisto.yml"
    shell:
        r"""
        kallisto index -i {output.idx} {input.fa}
        """


rule get_fastq_from_bam:
    input:
        bam="data/{sample_id}.bam",
    output:
        fq1="fastq/{sample_id}_1.fq.gz",
        fq2="fastq/{sample_id}_2.fq.gz",
    shell:
        r"""
        samtools collate -@ 8 -u -f --no-PG {input.bam} -O \
        | samtools fastq -@ 8 -1 {output.fq1} -2 {output.fq2}
        """


rule kallisto_quant:
    input:
        idx="kallisto/{sample_id}.idx",
        fq=["fastq/{sample_id}_1.fq.gz", "fastq/{sample_id}_2.fq.gz"],
    output:
        "kallisto/{sample_id}/pseudoalignments.bam",
    conda:
        "env/kallisto.yml"
    shell:
        r"""
        kallisto quant --threads 24 --pseudobam -o kallisto/{wildcards.sample_id} -i {input.idx} {input.fq}
        """


rule read_to_transcripts_tsv:
    input:
        bam="kallisto/{sample_id}/pseudoalignments.bam",
        gtf="stringtie/{sample_id}.gtf",
    output:
        tsv="kallisto/{sample_id}/read_transcripts.tsv.gz",
    shell:
        r"""
        {workflow.basedir}/scripts/read_to_transcripts_tsv.py \
            --bam {input.bam} \
            --gtf {input.gtf} \
        | gzip > {output.tsv}
        """


# rule kallisto_sort:
#     input:
#         bam='kallisto/{sample_id}/pseudoalignments.bam',
#     output:
#         bam='kallisto/{sample_id}/pseudoalignments.sort.bam',
#     shell:
#         r"""
#         samtools sort -@ 8 {input.bam} > {output.bam}
#         """
#
#
# rule index_bam:
#     input:
#         bam='kallisto/{sample_id}/pseudoalignments.sort.bam',
#     output:
#         bam='kallisto/{sample_id}/pseudoalignments.sort.bam.bai',
#     shell:
#         r"""
#         samtools index -@ 8 {input.bam}
#         """
#
#
# rule bwa_index:
#     input:
#         fa='stringtie/{sample_id}.fa',
#     output:
#         idx='stringtie/{sample_id}.fa.bwt',
#
# rule bwa_mem:
#     input:
#         fa='stringtie/{sample_id}.fa',
#         idx='stringtie/{sample_id}.fa.bwt',
#         fq=['data/fastq/ERR11178264_1.fastq.gz', 'data/fastq/ERR11178264_2.fastq.gz'],
#     output:
#         bam='bwa/{sample_id}.bam',
#     shell:
#         r"""
#         bwa mem -t 24 {input.fa} {input.fq} \
#         | samtools view -b > {output.bam}
#         """
#
#
#rule download:
#    output:
#        "ref/schistosoma_mansoni.PRJEA36577.WBPS19.genomic_softmasked.fa",
#        "schistosoma_mansoni.PRJEA36577.WBPS19.annotations.gff3",
#    shell:
#        r"""
#        cd ref
#        wget https://ftp.ebi.ac.uk/pub/databases/wormbase/parasite/releases/WBPS19/species/schistosoma_mansoni/PRJEA36577/schistosoma_mansoni.PRJEA36577.WBPS19.genomic_softmasked.fa.gz
#        wget https://ftp.ebi.ac.uk/pub/databases/wormbase/parasite/releases/WBPS19/species/schistosoma_mansoni/PRJEA36577/schistosoma_mansoni.PRJEA36577.WBPS19.annotations.gff3.gz
#        gunzip schistosoma_mansoni.PRJEA36577.WBPS19.genomic_softmasked.fa.gz
#        gunzip schistosoma_mansoni.PRJEA36577.WBPS19.annotations.gff3.gz
#        samtools faidx ref/schistosoma_mansoni.PRJEA36577.WBPS19.genomic_softmasked.fa
#        """


