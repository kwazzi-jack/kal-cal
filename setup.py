import setuptools

with open("README.md", "r", encoding="utf-8") as file:
    long_description = file.read()

requirements = [
    "codex-africanus==0.2.10",
    "dask>=2021.1.0",
    "dask-ms>=0.2.6",
    "llvmlite==0.35.0",
    "matplotlib>=3.3.4",
    "numba>=0.52.0",
    "numpy>=1.19.5",
    "astro-tigger>=1.5.0",
    "astro-tigger-lsm>=1.6.0",
    "astropy>=4.1",
    "pytest>=6.2.2",
    "pytest-forked>=1.3.0",
    "pytest-xdist>=2.2.0",
    "python-casacore>=3.3.1",
    "PyYAML>=5.3.1",
    "scipy>=1.5.4",
    "simms>=1.2.0",
    "Tigger>=0.1.1",
    "xarray>=0.16.2",
    "tqdm>=4.56.0",
    "packratt==0.1.2"
]

setuptools.setup(
    name="kal-cal", # Replace with your own username
    version="0.0.1",
    author="Brian Welman",
    author_email="brianallisterwelman@gmail.com",
    description="kalman Filter and Smoother"\
                + "Radio Interoferometric Calibration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/brianwelman2/kal-cal.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        'Programming Language :: Python :: 3.6'
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    test_suite='tests',
    install_requires=requirements
)