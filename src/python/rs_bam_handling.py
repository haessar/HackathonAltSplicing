import pysam
import pysam.samtools
import csv
import os
import pathlib

def bamTagHanding(bamFile, threadNumber = 1, output = False, sortTarget = "CB", mapping = False):
    # function takes unsorted bamFile and produces a split based upon tags
    # expected inputs:
    # bamFile: string of input file name 
    # output: optional input to add prefix to all output files 
    # sort target: default value CB: the tag which the sorting and spliting will be based upon 
    # mapping: if multiple values of target tag are to be grouped together. 
    # Accepts input as dictionary of form {grouping : [tag_value1, ..., tag_valueN]} or as csv file where first column is grouping and other columns are tag values 
    # output is set of files split as requested.  
    # Without mapping file split file based upon tag of form (output_) sortTarget value of tag.bam
    # If mapping file is used temporary files will be created and deleted from complete split of the tag 
    # final input will be of form (output_) grouping.bam 
    # if any of tags are not present in the groupings they will be left as temp files
    # will place results in directory named output_tag_files or the bamfile- ".bam" _tag_files
    if output:
        directoryName = output+ "__tag_files"
    else:
        directoryName = bamFile[0:-4] + "_tag_files"
    if not os.path.exists(directoryName):
        os.makedirs(directoryName)
    dirPath = str(pathlib.Path().resolve()) + "/" + directoryName + "/"
    if mapping:
        mappingTagsMissing = []
        pysam.samtools.split(bamFile, "-d", sortTarget, "-@", str(threadNumber), "-u", dirPath + "untagged.bam", "--output-fmt", "BAM", "-f", dirPath + ("'" + sortTarget + "%!.bam'").replace("-", "_"), catch_stdout=False)
        tempFiles = []
        if mapping.type() == dict:
            if output:
                for cellType in mapping.keys:
                    targetList = [dirPath + sortTarget + tag + ".bam" for tag in mapping[cellType]]
                    tempFiles.extend[targetList]
                    for target in targetList:
                        if not os.path.exists(target):
                            mappingTagsMissing.append[target]
                            targetList.remove(target)
                    pysam.merge("-f", "-@", threadNumber, "-o", dirPath + output + cellType + ".bam", *targetList)
            else:
                for cellType in mapping.keys:
                    targetList = [dirPath + sortTarget + tag + ".bam" for tag in mapping[cellType]]
                    tempFiles.extend[targetList]
                    for target in targetList:
                        if not os.path.exists(target):
                            mappingTagsMissing.append[target]
                            targetList.remove(target)
                    pysam.merge("-f", "-@", threadNumber,  "-o", dirPath + cellType + ".bam", *targetList)
        else:
            mappingDict = {}
            with open(mapping, newline="") as mappingFile:
                reader = csv.reader(mappingFile, delimiter=",")
                for mapRow in reader:
                    mappingDict[mapRow[0]] = mapRow[1:-1]
            
            if output:
                for cellType in mappingDict.keys:
                    targetList = [dirPath + sortTarget + tag + ".bam" for tag in mappingDict[cellType]]
                    tempFiles.extend[targetList]
                    for target in targetList:
                        if not os.path.exists(target):
                            mappingTagsMissing.append[target]
                            targetList.remove(target)
                    pysam.merge("-f", "-@", threadNumber, "-o", dirPath + output + cellType + ".bam", *targetList)
            else:
                for cellType in mappingDict.keys:
                    targetList = [dirPath + sortTarget + tag + ".bam" for tag in mappingDict[cellType]]
                    tempFiles.extend[targetList]
                    for target in targetList:
                        if not os.path.exists(target):
                            mappingTagsMissing.append[target]
                            targetList.remove(target)
                    pysam.merge("-f", "-@", threadNumber, "-o", dirPath + cellType + ".bam", *targetList)
        for tempFile in tempFiles:
            if os.path.exists(tempFile):
                os.remove(tempFile)
        
    else:
        if output:
            pysam.samtools.split(bamFile, "-d", sortTarget, "-@", str(threadNumber), "-u", dirPath + "untagged.bam", "--output-fmt", "BAM", "-f", dirPath + ("'" + output + "_" + sortTarget + "%!.bam'").replace("-", "_"), catch_stdout=False)
        else:
            pysam.samtools.split(bamFile, "-d", sortTarget, "-@", str(threadNumber), "-u", dirPath + "untagged.bam", "--output-fmt", "BAM", "-f", dirPath + ("'"+ sortTarget + "%!.bam'").replace("-", "_"), catch_stdout=False)
