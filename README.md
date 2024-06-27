# PLINK BED reader<!-- omit in toc -->
**Lightweight and memory efficient reader for PLINK BED files**. It supports both SNP-major and individual-major formats. Written in pure Python. Check the [available documentation](https://computational-genomics-bsc.github.io/plink-bed-reader/) for more information.

## Table of contents<!-- omit in toc -->
- [Getting started](#getting-started)
  - [Installation](#installation)
- [Usage](#usage)
- [Dependencies](#dependencies)


## Getting started
### Installation
VariantExtractor is available on PyPI and can be installed using `pip`:
```bash
pip install plink-bed-reader
```

## Usage
```python
# Import the package
from plink_bed_reader import PLINKBEDReader, BEDMode

# Load the PLINK BED file (we include the mode for sanity check, but it is optional)
bed = PLINKBEDReader('./input_test_data/test.bed', mode=BEDMode.SNP_MAJOR)

# Print the number of SNPs and samples
print('Number of SNPs:', bed.snp_count)
print('Number of samples:', bed.sample_count)
# Print the first SNP
first_snp = bed[0]
print('First SNP:', first_snp, first_snp.dtype)
# Print the first 3 SNPs
print('First 3 SNPs:', bed[:3])
```

## Dependencies

The dependencies are covered by their own respective licenses as follows:

* [Python/NumPy package](https://numpy.org/)
