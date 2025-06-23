# pylint: disable=no-member
import pysam
import pysam.samtools
import os
import os.path
from pathlib import Path
import pandas as pd
from tqdm import tqdm
from collections import defaultdict


def bamTagHandling(bamFile, threadNumber = 7, output = False, sortTarget = "CB", mapping = False, delim = ",", mappingColumns = ["Cluster", "cell_barcode"], untagged = False, unmapped = False ):
    '''
    # function takes unsorted bamFile and produces a split based upon tags
    # expected inputs:
    # bamFile: string of input file name 
    # output: optional input to add prefix to all output files 
    # sortTarget: default value CB: the tag which the sorting and spliting will be based upon 
    # mapping: if multiple values of target tag are to be grouped together. 
    # Accepts input as dictionary of form {grouping : [tag_value1, ..., tag_valueN]} 
    # or as a delimited file where first column is tag value and second columns are the group which the tag belongs to 
    # sep is the delimiter of the file
    # output is set of files split as requested.  
    # Without mapping file split file based upon tag of form (output_) sortTarget value of tag.bam
    # If mapping file is used final outputs will be of form (output_) grouping.bam 
    # will place results in directory named output
    # untagged: capture reads that don't contain a tag sortTarget in untagged.bam (default False)
    # unmapped: capture reads that do contain a tag sortTarget but not matched in mapping (default False)
    '''
    if output:
        directoryName = output+ "_files"
    else:
        directoryName = os.path.basename(bamFile)[0:-4] + "_tag_files"
    dirPath = str(Path().resolve()) + "/" + directoryName + "/"
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)
    if mapping:
        presentSet = set()
        if isinstance(mapping, dict):
            mappingDict = mapping.copy()
        else:
            mappingDict = {}
            mappingDf = pd.read_csv(mapping, sep = delim)
            clusters =  mappingDf[mappingColumns[0]].unique()
            for cluster in clusters:
                mappingDict[cluster] = mappingDf.loc[mappingDf[mappingColumns[0]] == cluster][mappingColumns[1]].unique()

        tag_to_cellType = {tag: ct for ct, tags in mappingDict.items() for tag in tags}
        with pysam.AlignmentFile(bamFile, "rb") as in_bam:
            total_reads = sum(total_count for _, _, _, total_count in in_bam.get_index_statistics())
            # We will open each cell-type BAM the first time we need it
            out_handles = {}
            counts = defaultdict(int)
            untagged_count = 0
            unmapped_count = 0

            if untagged:
                untagged_bam = pysam.AlignmentFile(dirPath + "untagged.bam", "wb", header=in_bam.header)
            if unmapped:
                unmapped_bam = pysam.AlignmentFile(dirPath + "unmapped.bam", "wb", header=in_bam.header)
            for read in tqdm(in_bam, total=total_reads):
                if not read.has_tag(sortTarget):
                    untagged_count += 1
                    if untagged:
                        untagged_bam.write(read)
                    continue
                tag = read.get_tag(sortTarget)

                if tag not in tag_to_cellType:
                    unmapped_count += 1
                    if unmapped:
                        unmapped_bam.write(read)
                    continue

                presentSet.add(tag)
                cellType = tag_to_cellType[tag]
                if cellType not in out_handles:  # lazily create handle
                    outFile = cellType.replace(" ", "_") + ".bam"
                    if output:
                        outFile = output + "_" + outFile
                    out_handles[cellType] = pysam.AlignmentFile(dirPath + outFile, "wb",
                                                        header=in_bam.header)
                out_handles[cellType].write(read)
                counts[cellType] += 1

        # close everything and report
        for h in out_handles.values():
            h.close()
        if untagged:
            untagged_bam.close()
        if unmapped:
            unmapped_bam.close()

        for cellType, n in counts.items():
            print(f"{cellType} : {n} reads")
        print(f"% of mapping tags found in BAM: {round(100 * len(presentSet) / len(mappingDf), 2)}")
        print(f'% of reads without a "{sortTarget}" tag: {round(100 * untagged_count / total_reads, 2)}')
        print(f'% of tagged reads without a mapping: {round(100 * unmapped_count / (total_reads - untagged_count), 2)}')
        
    else:
        if output:
            pysam.samtools.split(bamFile, "-d", sortTarget, "-@", str(threadNumber), "-u", dirPath + "untagged.bam", "--output-fmt", "BAM", "-f", dirPath + (output + "_" + sortTarget + "%!.bam").replace("-", "_"), catch_stdout=False)
        else:
            pysam.samtools.split(bamFile, "-d", sortTarget, "-@", str(threadNumber), "-u", dirPath + "untagged.bam", "--output-fmt", "BAM", "-f", dirPath + (sortTarget +"_" + "%!.bam").replace("-", "_"), catch_stdout=False)
