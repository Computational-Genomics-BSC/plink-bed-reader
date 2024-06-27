# Copyright 2024 - Barcelona Supercomputing Center
# Author: Rodrigo Martin
# MIT License

if __name__ == '__main__':
    import os
    import sys
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)) + '/../src/')
    from plink_bed_reader import PLINKBEDReader, BEDMode

    # Load the PLINK BED file
    bed = PLINKBEDReader('./input_test_data/test.bed', mode=BEDMode.SNP_MAJOR)

    # Print the number of SNPs and samples
    print('Number of SNPs:', bed.snp_count)
    print('Number of samples:', bed.sample_count)
    # Print the first SNP
    first_snp = bed[0]
    print('First SNP:', first_snp, first_snp.dtype)
    # Print the first 3 SNPs
    print('First 3 SNPs:', bed[:3])
