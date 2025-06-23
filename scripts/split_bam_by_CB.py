#!/usr/bin/env python3
import sys

from bam_manipulation.rs_bam_handling import bamTagHandling


if __name__ == "__main__":
    in_bam = sys.argv[1]
    mapping = sys.argv[2]
    bamTagHandling(in_bam, mapping=mapping, unmapped=True, untagged=True)
