#!/usr/bin/env python3

import argparse
import pysam
import re

parser = argparse.ArgumentParser(
    description="Prepare a tsv file with read name, transcript_id, gene_id"
)

parser.add_argument(
    "--bam", "-b", help="Input bam file, typically from kallisto --pseudobam"
)
parser.add_argument("--gtf", "-g", help="GTF file, typically from stringtie")
parser.add_argument(
    "--prob-assignment",
    "-p",
    help="Keep reads where the ZW tag (posterior probability of assignment) is at least this much [%(default)s]",
    default=0.8,
    type=float,
)
parser.add_argument('--version', '-v', action='version',
                    version='%(prog)s 0.2.0')
args = parser.parse_args()

tx2gene = {}

with open(args.gtf) as gtf:
    for line in gtf:
        if line.startswith("#"):
            continue
        line = line.strip().split("\t")
        if line[2] == "transcript":
            attrs = line[8].split(";")
            tx_id = None
            gene_id = None
            for x in attrs:
                x = x.strip()
                if x.startswith("transcript_id "):
                    tx_id = re.sub('"', "", x)
                    tx_id = tx_id.split(" ")[1]
                if x.startswith("gene_id "):
                    gene_id = re.sub('"', "", x)
                    gene_id = gene_id.split(" ")[1]
            tx2gene[tx_id] = gene_id

sam = pysam.AlignmentFile(args.bam)
print("\t".join(["#read_id", "transcript_id", "gene_id", "prob_assignment_zw"]))
for aln in sam:
    if aln.has_tag("ZW") and aln.get_tag("ZW") >= args.prob_assignment:
        out = [aln.query_name, aln.reference_name, tx2gene[aln.reference_name], str(aln.get_tag("ZW"))]
        print("\t".join(out))
