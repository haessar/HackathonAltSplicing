#!/usr/bin/env python3
# pylint: disable=no-member
"""
Module: bam_isoform_tagger

Provides functions to add isoform cluster ID tags to reads in a BAM file.
Clusters are defined as unique transcripts within each gene, assigning a numeric index per gene.
Includes a CLI interface.
"""

import argparse
import pysam
import os
import sys
from collections import defaultdict, OrderedDict


def load_cluster_map(cluster_file, read_col=1, gene_col=2, transcript_col=3, delimiter='\t'):
    """
    Load read-to-transcript mapping from a TSV, then assign numeric cluster IDs per gene.

    Args:
        cluster_file (str): Path to TSV file.
        read_col (int): 1-based index of column containing read names.
        gene_col (int): 1-based index of column containing gene IDs.
        transcript_col (int): 1-based index of column containing transcript IDs.
        delimiter (str): Column delimiter (default tab).

    Returns:
        dict: Mapping {read_id: cluster_id_int} where cluster IDs are assigned within each gene.

    Raises:
        FileNotFoundError: If the cluster_file does not exist.
        ValueError: If any line does not contain enough columns.
    """
    if not os.path.isfile(cluster_file):
        raise FileNotFoundError(f"Cluster file not found: '{cluster_file}'")
    if read_col < 1 or gene_col < 1 or transcript_col < 1:
        raise ValueError("Column indices must be 1 or greater.")

    # Temporary storage: for each gene, maintain an ordered set of transcripts
    gene_transcripts = OrderedDict()  # gene -> OrderedDict of transcript->None
    read_to_info = {}

    with open(cluster_file, 'r') as fh:
        for line_num, line in enumerate(fh, start=1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split(delimiter)
            max_idx = max(read_col, gene_col, transcript_col)
            if len(parts) < max_idx:
                raise ValueError(
                    f"Line {line_num} in '{cluster_file}' has {len(parts)} columns, "
                    f"but read_col={read_col}, gene_col={gene_col}, transcript_col={transcript_col} require at least {max_idx} columns."
                )
            read_name = parts[read_col - 1]
            gene_id = parts[gene_col - 1]
            transcript_id = parts[transcript_col - 1]

            if gene_id not in gene_transcripts:
                gene_transcripts[gene_id] = OrderedDict()
            # Record transcript order within gene
            if transcript_id not in gene_transcripts[gene_id]:
                gene_transcripts[gene_id][transcript_id] = None

            read_to_info[read_name] = (gene_id, transcript_id)

    # Assign numeric index for each transcript per gene
    gene_cluster_idx = {}  # gene -> {transcript: index}
    for gene_id, transcripts in gene_transcripts.items():
        gene_cluster_idx[gene_id] = {}
        for idx, transcript_id in enumerate(transcripts.keys(), start=1):
            gene_cluster_idx[gene_id][transcript_id] = idx

    # Build final read->cluster_id mapping
    read_to_cluster = {}
    for read_name, (gene_id, transcript_id) in read_to_info.items():
        cid = gene_cluster_idx[gene_id].get(transcript_id, 0)
        read_to_cluster[read_name] = cid

    return read_to_cluster


def add_isoform_tags(input_bam, output_bam, cluster_map=None):
    """
    Add isoform cluster ID tags (IC:i:<cluster_id>) to reads in a BAM file.

    Args:
        input_bam (str): Path to input BAM (coordinate-sorted, indexed).
        output_bam (str): Path to output BAM to write.
        cluster_map (dict, optional): Mapping {read_name: cluster_id}. If None, uses dummy logic.
    """
    try:
        bam_in = pysam.AlignmentFile(input_bam, "rb")
    except Exception as e:
        sys.exit(f"Error opening input BAM '{input_bam}': {e}")

    header = bam_in.header.to_dict()
    header.setdefault("CO", []).append("IC:i: Isoform cluster ID assigned by bam_isoform_tagger")

    try:
        bam_out = pysam.AlignmentFile(output_bam, "wb", header=header)
    except Exception as e:
        sys.exit(f"Error creating output BAM '{output_bam}': {e}")

    for read in bam_in.fetch(until_eof=True):
        # Retain unmapped or secondary/supplementary reads without tag
        if read.is_unmapped or read.is_secondary or read.is_supplementary:
            bam_out.write(read)
            continue

        if cluster_map is not None:
            cid = cluster_map.get(read.query_name, 0)
        else:
            try:
                chrom = read.reference_name
                num = int(chrom.replace("chr", "")) if chrom.startswith("chr") else 0
                cid = num % 10
            except Exception:
                cid = 0

        read.set_tag("IC", cid, value_type="i")
        bam_out.write(read)

    bam_in.close()
    bam_out.close()

    try:
        pysam.index(output_bam)
    except Exception as e:
        sys.exit(f"Error indexing output BAM '{output_bam}': {e}")


def parse_args(argv=None):
    """
    Parse command-line arguments for the script.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Add isoform cluster ID tags to BAM reads, clustering transcripts per gene"
    )
    parser.add_argument(
        "-i", "--input", required=True,
        help="Input BAM (coordinate-sorted, indexed)"
    )
    parser.add_argument(
        "-o", "--output", required=True,
        help="Output BAM with IC tag"
    )
    parser.add_argument(
        "-c", "--cluster_file", required=True,
        help="TSV mapping read name, gene ID, transcript ID per line"
    )
    parser.add_argument(
        "--read_col", type=int, default=1,
        help="1-based column number for read names in TSV (default: 1)"
    )
    parser.add_argument(
        "--gene_col", type=int, default=2,
        help="1-based column number for gene IDs in TSV (default: 2)"
    )
    parser.add_argument(
        "--transcript_col", type=int, default=3,
        help="1-based column number for transcript IDs in TSV (default: 3)"
    )
    parser.add_argument(
        "--delimiter", default="\t",
        help="Column delimiter in TSV (default: tab)"
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    try:
        cluster_map = load_cluster_map(
            args.cluster_file,
            read_col=args.read_col,
            gene_col=args.gene_col,
            transcript_col=args.transcript_col,
            delimiter=args.delimiter
        )
    except Exception as e:
        sys.exit(f"Error loading cluster map: {e}")

    add_isoform_tags(
        input_bam=args.input,
        output_bam=args.output,
        cluster_map=cluster_map
    )

    print(f"Written and indexed: {args.output}")


if __name__ == "__main__":
    main(sys.argv[1:])
