from setuptools import setup, find_packages

__version__ = "1.0.1"
__author__ = 'Rapsssito'

if __name__ == '__main__':
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()

    with open("requirements.txt", "r", encoding="utf-8") as f:
        requirements = f.read().splitlines()

    with open("src/plink_bed_reader/__init__.py", "r", encoding="utf-8") as fd:
        init_content = fd.read()
    version = __version__
    author = __author__

    setup(
        name='plink-bed-reader',
        version=version,
        author=author,
        author_email='contact@rodrigomartin.dev',
        description='Lightweight and memory efficient reader for PLINK BED files. It supports both SNP-major and individual-major formats. Written in pure Python.',
        keywords='bed plink genetics bioinformatics variant indel snv genotype',
        long_description=long_description,
        long_description_content_type='text/markdown',
        url='https://github.com/Computational-Genomics-BSC/plink-bed-reader',
        project_urls={
            'Bug Tracker': 'https://github.com/Computational-Genomics-BSC/plink-bed-reader/issues',
        },
        classifiers=[
            'Programming Language :: Python :: 3 :: Only',
            'Development Status :: 5 - Production/Stable',
            'Operating System :: OS Independent'
        ],
        package_dir={'': 'src'},
        packages=find_packages(where="src"),
        python_requires='>= 3.6',
        install_requires=requirements,
        extras_require={
            "docs": ["sphinx", "sphinx-rtd-theme", "myst_parser", "docutils>=0.18.0"],
        }
    )
