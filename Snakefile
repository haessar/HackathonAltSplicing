sample_id = os.path.basename(re.sub('\.bam', '', config['bam']))

rule all:
    input:
       expand('kallisto/{sample_id}/pseudoalignments.bam', sample_id=sample_id),
 

rule download:
    output:
        'ref/schistosoma_mansoni.PRJEA36577.WBPS19.genomic_softmasked.fa',
        'schistosoma_mansoni.PRJEA36577.WBPS19.annotations.gff3',
    shell:
        r"""
        cd ref
        wget https://ftp.ebi.ac.uk/pub/databases/wormbase/parasite/releases/WBPS19/species/schistosoma_mansoni/PRJEA36577/schistosoma_mansoni.PRJEA36577.WBPS19.genomic_softmasked.fa.gz
        wget https://ftp.ebi.ac.uk/pub/databases/wormbase/parasite/releases/WBPS19/species/schistosoma_mansoni/PRJEA36577/schistosoma_mansoni.PRJEA36577.WBPS19.annotations.gff3.gz
        gunzip schistosoma_mansoni.PRJEA36577.WBPS19.genomic_softmasked.fa.gz
        gunzip schistosoma_mansoni.PRJEA36577.WBPS19.annotations.gff3.gz
        samtools faidx ref/schistosoma_mansoni.PRJEA36577.WBPS19.genomic_softmasked.fa
        """


rule stringtie:
    input:
        bam='data/{sample_id}.bam',
        gff='ref/schistosoma_mansoni.PRJEA36577.WBPS19.annotations.gff3',
    output:
        gtf='stringtie/{sample_id}.gtf',
    shell:
        r"""
        stringtie -o {output.gtf} \
            -p 24 \
            -G {input.gff} \ 
            {input.bam} 
        """


rule fastaForTranscripts:
    input:
        gtf='stringtie/{sample_id}.gtf',
        genome='ref/schistosoma_mansoni.PRJEA36577.WBPS19.genomic_softmasked.fa',
    output:
        fa='stringtie/{sample_id}.fa',
    shell:
        r"""
        gffread -w {output.fa} \
            -g {input.genome} \
            {input.gtf}
        """


rule kallisto_index:
    input:
        fa='stringtie/{sample_id}.fa',
    output:
        idx='kallisto/{sample_id}.idx',
    conda:
        'env/kallisto.yml',
    shell:
        r"""
        kallisto index -i {output.idx} {input.fa}
        """


rule kallisto_quant:
    input:
        idx='kallisto/{sample_id}.idx',
        fq=['data/fastq/ERR11178264_1.fastq.gz', 'data/fastq/ERR11178264_2.fastq.gz'],
    output:
        'kallisto/{sample_id}/pseudoalignments.bam',
    conda:
        'env/kallisto.yml',
    shell:
        r"""
        kallisto quant --threads 24 --pseudobam -o kallisto/{wildcards.sample_id} -i {input.idx} {input.fq}
        """
