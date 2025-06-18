#!/usr/bin/env python3
# pylint: disable=no-member
import argparse
import pysam

def parse_args():
    parser = argparse.ArgumentParser(description="WP3: Add isoform cluster ID tags to BAM reads")
    parser.add_argument("-i", "--input", required=True, help="Input BAM (coordinate‐sorted, indexed)")
    parser.add_argument("-o", "--output", required=True, help="Output BAM with IC tag")
    parser.add_argument("-c", "--cluster_file", required=False,
                        help="Optional TSV mapping read name → cluster ID; else use dummy logic")
    return parser.parse_args()

def load_cluster_map(cluster_file):
    """
    Example cluster_file format:
      read_name    cluster_id
      read0001     5
      read0002     2
      ...
    Returns: dict {read_name: cluster_id_int}
    """
    cmap = {}
    with open(cluster_file) as fh:
        for line in fh:
            read_name, cid = line.strip().split()
            cmap[read_name] = int(cid)
    return cmap

def main():
    args = parse_args()
    bam_in = pysam.AlignmentFile(args.input, "rb")
    header = bam_in.header.to_dict()

    # Optionally add a comment about what IC means
    header.setdefault("CO", []).append("IC:i: Isoform cluster ID assigned by WP3 script")

    bam_out = pysam.AlignmentFile(args.output, "wb", header=header)

    cluster_map = {}
    if args.cluster_file:
        cluster_map = load_cluster_map(args.cluster_file)

    for read in bam_in.fetch(until_eof=True):
        # 1) Skip unmapped or secondary/supplementary reads
        if read.is_unmapped or read.is_secondary or read.is_supplementary:
            bam_out.write(read)
            continue

        # 2) Determine cluster ID
        # If provided a cluster map by read_name, use that; otherwise use dummy logic
        if cluster_map:
            cid = cluster_map.get(read.query_name, 0)
        else:
            # Dummy: assign cluster by chromosome (e.g., cluster = int(chrN[3:]) mod 10)
            try:
                chrom = read.reference_name  # e.g., "chr12"
                num = int(chrom.replace("chr", "")) if chrom.startswith("chr") else 0
                cid = num % 10
            except ValueError:
                cid = 0

        # 3) Set the IC tag
        read.set_tag("IC", cid, value_type="i")

        # 4) Write to output
        bam_out.write(read)

    bam_in.close()
    bam_out.close()

    # 5) Index the new BAM
    pysam.index(args.output)
    print(f"Written and indexed: {args.output}")

if __name__ == "__main__":
    main()
