#!/usr/bin/env python3
import sys

from bam_manipulation.merge_samples_by_celltype import merge_samples_by_celltype


if __name__ == "__main__":
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    merge_samples_by_celltype(input_dir, output_dir, threads=8)
