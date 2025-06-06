import pysam
import pysam.samtools
import csv
import os
from contextlib import chdir
import pathlib
from pathlib import Path
import pandas as pd

def bamTagHanding(bamFile, threadNumber = 7, output = False, sortTarget = "CB", mapping = False, delim = ",", mappingColumns = ["Clusters", "cell_barcode"] ):
    # function takes unsorted bamFile and produces a split based upon tags
    # expected inputs:
    # bamFile: string of input file name 
    # output: optional input to add prefix to all output files 
    # sort target: default value CB: the tag which the sorting and spliting will be based upon 
    # mapping: if multiple values of target tag are to be grouped together. 
    # Accepts input as dictionary of form {grouping : [tag_value1, ..., tag_valueN]} 
    # or as a delimited file with column names mappingColumns[0] = grouping column mappingColumns[1] = tag values
    # output is set of files split as requested.  
    # Without mapping file split file based upon tag of form (output_) sortTarget value of tag.bam
    # If mapping file is used temporary files will be created and deleted from complete split of the tag 
    # final input will be of form (output_) grouping.bam 
    # if any of tags are not present in the groupings they will be left as temp files
    # will place results in directory named output
    if output:
        directoryName = output+ "_files"
    else:
        directoryName = bamFile[0:-4] + "_tag_files"
    if not os.path.exists(directoryName):
        os.makedirs(directoryName)
    dirPath = str(pathlib.Path().resolve()) + "/" + directoryName + "/"
    if mapping:
        mappingTagsMissing = []
        pysam.samtools.split(bamFile, "-d", sortTarget, "-@", str(threadNumber), "-u", dirPath + "untagged.bam", "--output-fmt", "BAM", "-f", dirPath + ("'" + sortTarget + "%!.bam'"), catch_stdout=False)
        tempFiles = []
        if type(mapping) == dict:
            if output:
                for cellType in mapping.keys():
                    targetList = [dirPath + ("'" + "_" + tag + ".bam'") for tag in mapping[cellType]]
                    tempFiles.extend(targetList)
                    for target in targetList:
                        if not Path(target).is_file():
                            mappingTagsMissing.append(target)
                            targetList.remove(target)
                    print(targetList)
                    pysam.merge("-f", "-@", str(threadNumber), "-o", dirPath + output + cellType + ".bam", *targetList)
            else:
                for cellType in mapping.keys():
                    targetList = [dirPath + ("'"+ tag + ".bam'")  for tag in mapping[cellType]]
                    tempFiles.extend(targetList)
                    for target in targetList:
                        if not Path(target).is_file():
                            mappingTagsMissing.append(target)
                            targetList.remove(target)
                    print(targetList)
                    pysam.merge("-f", "-@", str(threadNumber),  "-o", dirPath + cellType + ".bam", *targetList)
        else:
            mappingDict = {}
            mappingDf = pd.read_csv(mapping, sep = delim)
            clusters =  mappingDf[mappingColumns[0]].unique()
            for cluster in clusters:
                mappingDict[cluster] = mappingDf.loc[mappingDf[mappingColumns[0]] == cluster][mappingColumns[1]].unique()

            if output:
                for cellType in mappingDict.keys():
                    targetList = [dirPath + ("'"+ + tag + ".bam'") for tag in mappingDict[cellType]]
                    tempFiles.extend(targetList)
                    for target in targetList:
                        if not Path(target).is_file():
                            print(target)
                            mappingTagsMissing.append(target)
                            targetList.remove(target)
                    print(targetList)
                    pysam.merge("-f", "-@", str(threadNumber), "-o", dirPath + output + cellType + ".bam", *targetList)
            else:
                for cellType in mappingDict.keys():
                    targetList = [dirPath + ("'"  + tag + ".bam'")  for tag in mappingDict[cellType]]
                    tempFiles.extend(targetList)
                    for target in targetList:
                        if not Path(target).is_file():
                            mappingTagsMissing.append(target)
                            targetList.remove(target)
                    pysam.merge("-f", "-@", str(threadNumber), "-o", dirPath + cellType + ".bam", *targetList)
        for tempFile in tempFiles:
            if os.path.exists(tempFile):
                os.remove(tempFile)
        print(mappingTagsMissing)
    else:
        if output:
            pysam.samtools.split(bamFile, "-d", sortTarget, "-@", str(threadNumber), "-u", dirPath + "untagged.bam", "--output-fmt", "BAM", "-f", dirPath + (output + "_" + sortTarget + "%!.bam").replace("-", "_"), catch_stdout=False)
        else:
            pysam.samtools.split(bamFile, "-d", sortTarget, "-@", str(threadNumber), "-u", dirPath + "untagged.bam", "--output-fmt", "BAM", "-f", dirPath + (sortTarget +"_" + "%!.bam").replace("-", "_"), catch_stdout=False)

