#!/usr/bin/env python3
"""
Module: bam_isoform_tagger

Provides functions to add isoform cluster ID tags to reads in a BAM file.
Includes a CLI interface.
"""

import argparse
import pysam
import os
import sys


def load_cluster_map(cluster_file, read_col=1, cluster_col=2, delimiter='\t'):
    """
    Load a mapping from read name to cluster ID from a TSV file with arbitrary columns.

    Args:
        cluster_file (str): Path to TSV file.
        read_col (int): 1-based index of column containing read names.
        cluster_col (int): 1-based index of column containing cluster IDs.
        delimiter (str): Column delimiter (default tab).

    Returns:
        dict: Mapping {read_name: cluster_id_int}

    Raises:
        FileNotFoundError: If the cluster_file does not exist.
        ValueError: If any line does not contain enough columns or cluster_id is not an integer.
    """
    if not os.path.isfile(cluster_file):
        raise FileNotFoundError(f"Cluster file not found: '{cluster_file}'")
    if read_col < 1 or cluster_col < 1:
        raise ValueError("Column indices must be 1 or greater.")

    cmap = {}
    with open(cluster_file, 'r') as fh:
        for line_num, line in enumerate(fh, start=1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue  # skip empty or commented lines
            parts = line.split(delimiter)
            max_idx = max(read_col, cluster_col)
            if len(parts) < max_idx:
                raise ValueError(
                    f"Line {line_num} in '{cluster_file}' has {len(parts)} columns, "
                    f"but read_col={read_col}, cluster_col={cluster_col} require at least {max_idx} columns."
                )
            read_name = parts[read_col - 1]
            cid_str = parts[cluster_col - 1]
            try:
                cid = int(cid_str)
            except ValueError:
                raise ValueError(
                    f"Invalid cluster ID on line {line_num} in '{cluster_file}': expected integer, got '{cid_str}'"
                )
            if read_name in cmap:
                raise ValueError(
                    f"Duplicate read name '{read_name}' found in '{cluster_file}' on line {line_num}"
                )
            cmap[read_name] = cid
    return cmap


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


def parse_args():
    """
    Parse command-line arguments for the script.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Add isoform cluster ID tags to BAM reads"
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
        "-c", "--cluster_file", required=False,
        help="Optional TSV mapping read name → cluster ID; if omitted, dummy logic is used"
    )
    parser.add_argument(
        "--read_col", type=int, default=1,
        help="1-based column number for read names in TSV (default: 1)"
    )
    parser.add_argument(
        "--cluster_col", type=int, default=2,
        help="1-based column number for cluster IDs in TSV (default: 2)"
    )
    parser.add_argument(
        "--delimiter", default="\t",
        help="Column delimiter in TSV (default: tab)"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    cluster_map = None
    if args.cluster_file:
        try:
            cluster_map = load_cluster_map(
                args.cluster_file,
                read_col=args.read_col,
                cluster_col=args.cluster_col,
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
    main()
