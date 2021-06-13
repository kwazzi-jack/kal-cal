import setuptools

with open("README.md", "r", encoding="utf-8") as file:
    long_description = file.read()

with open("requirements.txt", "r") as file:
    requirements = file.readlines()

setuptools.setup(
    name="kal-cal",
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
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
    ],
    python_requires='>=3.6',
    test_suite='tests',
    install_requires=requirements,
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "kal-calibrate = kalcal.cli.main:kalcal_calibrate",
            "kal-create = kalcal.cli.main:kalcal_create",
            "kal-plot = kalcal.cli.main:kalcal_plot"
            ]
    },
)