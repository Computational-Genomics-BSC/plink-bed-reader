# Copyright 2024 - Barcelona Supercomputing Center
# Author: Rodrigo Martin
# MIT License

from typing import Tuple, Optional, Any, Union
from enum import Enum, auto
import os
import io
import numpy as np


class BEDMode(Enum):
    """Enum with the possible modes of a BED file"""
    SNP_MAJOR = auto()
    INDIVIDUAL_MAJOR = auto()


def _get_major_mode(bed_file: io.BufferedReader) -> BEDMode:
    # Save byte position
    pos = bed_file.tell()
    # Read the mode byte to check if the file is in SNP major or individual major mode
    bed_file.seek(2, os.SEEK_SET)
    mode = bed_file.read(1)
    # Restore byte position
    bed_file.seek(pos, os.SEEK_SET)
    if mode == b'\x01':
        return BEDMode.SNP_MAJOR
    if mode == b'\x00':
        return BEDMode.INDIVIDUAL_MAJOR
    raise ValueError("Invalid mode byte")


def _read_sample_snp_counts(fam_file_path: str, bim_file_path: str) -> Tuple[int, int]:
    sample_count = 0
    snp_count = 0
    # Count the number of samples and SNPs in the file
    with open(fam_file_path, encoding='UTF-8') as fam_file:
        for _ in fam_file:
            sample_count += 1
    with open(bim_file_path, encoding='UTF-8') as bim_file:
        for _ in bim_file:
            snp_count += 1
    return sample_count, snp_count


class PLINKBEDReader():
    """
    Reads PLINK BED files (individual major or SNP major) and returns the genotypes as a NumPy array (uint8).
    The file is read in chunks to reduce memory usage and allows for random access.
    Matching the PLINK format specification (https://www.cog-genomics.org/plink/1.9/formats#bed), the genotypes are encoded as follows:
    0 = homozygous major
    1 = heterozygous
    2 = missing
    3 = homozygous minor
    """

    def __init__(self, bed_file_path: str, offset: int = 0, count: Optional[int] = None, mode: Optional[BEDMode] = None, fam_file_path: Optional[str] = None, bim_file_path: Optional[str] = None):
        """
        Parameters
        ----------
        bed_file_path : str
            Path to the BED file (can be with or without the extension). Admits both SNP major and individual major modes.
        offset : int, optional
            Number of samples or SNPs to skip at the beginning of the file, depending on the major mode.
        count : int, optional
            Number of samples or SNPs to read from the file, depending on the major mode.
        mode : BEDMode, optional
            Major mode of the file. The mode will be inferred from the file. If the mode is provided, it will be used as a sanity check.
        fam_file_path : str, optional
            Path to the FAM file. If not provided, it will be inferred from the BED file.
        bim_file_path : str, optional
            Path to the BIM file. If not provided, it will be inferred from the BED file.
        """
        bed_prefix = bed_file_path[:-4] if bed_file_path.endswith('.bed') else bed_file_path
        fam_file_path = bed_prefix + '.fam' if fam_file_path is None else fam_file_path
        bim_file_path = bed_prefix + '.bim' if bim_file_path is None else bim_file_path
        # Count the number of samples and SNPs in the file
        raw_sample_count, raw_snp_count = _read_sample_snp_counts(fam_file_path, bim_file_path)
        # Open the BED file
        self._bed_file = open(bed_prefix + '.bed', 'rb')
        # Check if the file is in SNP major or individual major mode
        self._major_mode = _get_major_mode(self._bed_file)
        # Check if the mode is correct
        if mode is not None and mode != self._major_mode:
            raise ValueError(f'Mismatch mode {mode} for file {self._major_mode}')
        self._offset = offset
        if self._major_mode == BEDMode.INDIVIDUAL_MAJOR:
            self._sample_count = raw_sample_count - offset if count is None else count
            self._snp_count = raw_snp_count
            # We are in individual major mode, so each byte contains 4 SNPs
            # The chunk size is rounded up to the nearest byte
            self.chunk_size_bytes = int(np.ceil(self._snp_count / 4))
        elif self._major_mode == BEDMode.SNP_MAJOR:
            self._sample_count = raw_sample_count
            self._snp_count = raw_snp_count - offset if count is None else count
            # We are in SNP major mode, so each byte contains 4 samples
            # The chunk size is rounded up to the nearest byte
            self.chunk_size_bytes = int(np.ceil(self._sample_count / 4))

    @property
    def sample_count(self):
        """Number of samples"""
        return self._sample_count

    @property
    def snp_count(self):
        """Number of SNPs"""
        return self._snp_count

    @property
    def major_mode(self):
        """Major mode of the file"""
        return self._major_mode

    def close(self):
        """Close the BED file"""
        self._bed_file.close()

    def _read_idx(self, idx: int) -> np.ndarray[Any, np.dtype[np.uint8]]:
        # Check if the file is closed
        if self._bed_file.closed:
            raise ValueError("I/O operation on closed BED file")
        # Check if the index is out of bounds
        if idx >= len(self):
            raise IndexError(f"Index out of bounds {idx} {len(self)}")

        # Skip the header (first 3 bytes are magic numbers and mode)
        self._bed_file.seek(3 + self.chunk_size_bytes * (idx + self._offset), os.SEEK_SET)

        # Read the chunk
        chunk = self._bed_file.read(self.chunk_size_bytes)
        if not chunk:
            raise ValueError("Unexpected end of BED file")
        # Convert the chunk to a NumPy array
        bit_array = np.frombuffer(chunk, dtype=np.uint8)
        del chunk
        # The array has one byte per SNP/Sample
        bit_array = np.unpackbits(bit_array)
        # The array is stored as two bits per SNP/Sample, but in reverse in each byte, sum them to get the array
        array = (bit_array[::2] + 2 * bit_array[1::2]).astype(np.uint8)
        del bit_array
        # Each block of 4 bit SNP/Sample is stored in reverse order
        # 0 = homozygous major
        # 1 = heterozygous
        # 2 = missing
        # 3 = homozygous minor
        # Reverse the order of the SNP/Sample in the block
        array = array.reshape(-1, 4)[:, ::-1]
        # Flatten the array
        array = array.flatten()
        # Remove the extra bits
        return array[:self._snp_count] if self._major_mode == BEDMode.INDIVIDUAL_MAJOR else array[:self._sample_count]

    def __len__(self):
        return self._sample_count if self._major_mode == BEDMode.INDIVIDUAL_MAJOR else self._snp_count

    def __getitem__(self, key: Union[int, slice]):
        if isinstance(key, slice):
            return np.array([self._read_idx(i) for i in range(*key.indices(len(self)))], dtype=np.uint8)
        return self._read_idx(key)
