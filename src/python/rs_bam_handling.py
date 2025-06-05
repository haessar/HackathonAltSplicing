import pysam
import pysam.samtools
import csv
import os

def bamTaghanding(bamFile, output = False, sortTarget = "CB", mapping = False):
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

    if mapping:
        pysam.samtools.split("-d", sortTarget, "--output-fmt", "bam", "-f", "-u", bamFile, "'temp_" + sortTarget + "%!.bam'", catch_stdout=False)
        tempFiles = []
        if mapping.type() == dict:
            if output:
                for cellType in mapping.keys:
                    targetList = ["temp_"  + sortTarget + tag + ".bam" for tag in mapping[cellType]]
                    tempFiles.extend[targetList]
                    pysam.merge("-f", "-o", output + cellType + ".bam", *targetList)
            else:
                for cellType in mapping.keys:
                    targetList = ["temp_"  + sortTarget + tag + ".bam" for tag in mapping[cellType]]
                    tempFiles.extend[targetList]
                    pysam.merge("-f", "-o", cellType + ".bam", *targetList)
        else:
            mappingDict = {}
            with open(mapping, newline="") as mappingFile:
                reader = csv.reader(mappingFile, delimiter=",")
                for mapRow in reader:
                    mappingDict[mapRow[0]] = mapRow[1:-1]
            
            if output:
                for cellType in mappingDict.keys:
                    targetList = ["temp_" + sortTarget + tag + ".bam" for tag in mappingDict[cellType]]
                    tempFiles.extend[targetList]
                    pysam.merge("-f", "-o", output + cellType + ".bam", *targetList)
            else:
                for cellType in mappingDict.keys:
                    targetList = ["temp_" + sortTarget + tag + ".bam" for tag in mappingDict[cellType]]
                    tempFiles.extend[targetList]
                    pysam.merge("-f", "-o", cellType + ".bam", *targetList)
        for tempFile in tempFiles:
            if os.path.exists(tempFile):
                os.remove(tempFile)
        
    else:
        if output:
            pysam.samtools.split("-d", sortTarget, "--output-fmt", "bam", "-f", "-u", bamFile, "'" + output + "_" + sortTarget + "%!.bam'", catch_stdout=False)
        else:
            pysam.samtools.split("-d", sortTarget, "--output-fmt", "bam", "-f", "-u", bamFile, "'" + sortTarget + "%!.bam'", catch_stdout=False)
