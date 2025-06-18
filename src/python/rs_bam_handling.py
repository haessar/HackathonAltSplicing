import pysam
import pysam.samtools
import os
import os.path
from pathlib import Path
import pandas as pd


def bamTagHandling(bamFile, threadNumber = 7, output = False, sortTarget = "CB", mapping = False, delim = ",", mappingColumns = ["Cluster", "cell_barcode"] ):
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
    # If mapping file is used temporary files will be created and deleted from complete split of the tag 
    # final input will be of form (output_) grouping.bam 
    # if any of tags are not present in the groupings they will be left as temp files
    # will place results in directory named output
    '''
    if output:
        directoryName = output+ "_files"
    else:
        directoryName = os.path.basename(bamFile)[0:-4] + "_tag_files"
    dirPath = str(Path().resolve()) + "/" + directoryName + "/"
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)
    if mapping:
        mappingTagsMissing = []
        pysam.samtools.split(bamFile, "-d", sortTarget, "-@", str(threadNumber), "-u", dirPath + "untagged.bam", "--output-fmt", "BAM", "-f", dirPath + ("'" + "%!.bam'"), catch_stdout=False)
        tempFiles = []
        if isinstance(mapping, dict):
            mappingDict = mapping.copy()
        else:
            mappingDict = {}
            mappingDf = pd.read_csv(mapping, sep = delim)
            clusters =  mappingDf[mappingColumns[0]].unique()
            for cluster in clusters:
                mappingDict[cluster] = mappingDf.loc[mappingDf[mappingColumns[0]] == cluster][mappingColumns[1]].unique()

        for cellType, tags in mappingDict.items():
            outFile = cellType.replace(" ", "_") + ".bam"
            if output:
                outFile = output + "_" + outFile
            targetList = [dirPath + ("'" + tag + ".bam'")  for tag in tags]
            tempFiles.extend(targetList)
            presentList = [tag for tag in targetList if Path(tag).is_file()]
            mappingTagsMissing.extend(list(set(targetList)- set(presentList)))
            if len(presentList) > 0:
                pysam.merge("-f", "-@", str(threadNumber), "-o", dirPath + outFile, *presentList)
        for tempFile in tempFiles:
            if os.path.exists(tempFile):
                os.remove(tempFile)
        if len(mappingTagsMissing) > 0:
            mappingTagsMissing = [tagNotPresent.split("/")[-1].strip("'")[0:-4] for tagNotPresent in mappingTagsMissing]
            print("Following labelled cells missing in data ")
            print(mappingTagsMissing)
        
    else:
        if output:
            pysam.samtools.split(bamFile, "-d", sortTarget, "-@", str(threadNumber), "-u", dirPath + "untagged.bam", "--output-fmt", "BAM", "-f", dirPath + (output + "_" + sortTarget + "%!.bam").replace("-", "_"), catch_stdout=False)
        else:
            pysam.samtools.split(bamFile, "-d", sortTarget, "-@", str(threadNumber), "-u", dirPath + "untagged.bam", "--output-fmt", "BAM", "-f", dirPath + (sortTarget +"_" + "%!.bam").replace("-", "_"), catch_stdout=False)
