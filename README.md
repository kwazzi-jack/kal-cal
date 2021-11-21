# kal-cal
## Kalman Filter and Smoother RI Calibration

**kal-cal** is a Python library developed to provide proof-of-concept tools for *Kalman Filtering and Smoothing Theory* (see [Bayesian Filtering and Smoothing by Simo S ̈arkk ̈a](https://users.aalto.fi/~ssarkka/pub/cup_book_online_20131111.pdf)) as a replacement calibration framework for *Radio-Interoferometric Gains Calibration* (see [Non-linear Kalman Filters for calibration in radio interferometry by Cyril Tasse](https://arxiv.org/abs/1403.6308)). This library is part of the master's thesis work of *Brian Welman* (@[brianWelman2](https://github.com/brianwelman2) on github) through [Radio Astronomy Techniques and Technologies](http://www.ratt-ru.org/) under [SARAO](https://www.sarao.ac.za/) during the period of 2020 to 2021.

## Requirements
The only external requirement is the `simms` which can be installed via `pip` and `apt`. Otherwise, all Python packages are listed in [`requirements.txt`](https://github.com/brianwelman2/kal-cal/blob/main/requirements.txt) and are installed when **kal-cal** is installed.

## Installation

Firstly, you need at least `python3`, or even better `python3.6`, as this is the version the library was developed on. Use the package manager [`pip`](https://pip.pypa.io/en/stable/) to install **kal-cal** as follows:

```bash
pip install https://github.com/brianwelman2/kal-cal/archive/refs/heads/main.zip
```

## Usage
To import **kal-cal**:
```python
import kalcal
```

Within `kalcal` exists the following subsections:

- [`calibration`](https://github.com/brianwelman2/kal-cal/tree/main/kalcal/calibration) - Filter and Smoother algorithms to calibrate for gains,
- [`cli`](https://github.com/brianwelman2/kal-cal/tree/main/kalcal/cli) - Command-Line Interface section that houses the commands for **kal-cal**,
- [`create`](https://github.com/brianwelman2/kal-cal/tree/main/kalcal/create) - Simulation functions for measurement sets, gains and visibilities,
- [`datasets`](https://github.com/brianwelman2/kal-cal/tree/main/kalcal/datasets) - Pre-defined datasets such as sky-models and antenna tables,
- [`examples`](https://github.com/brianwelman2/kal-cal/tree/main/kalcal/examples) - Quick tutorials on how to utilize some of the basic functionality of **kal-cal**, both as an API and a CLI,
- [`filters`](https://github.com/brianwelman2/kal-cal/tree/main/kalcal/filters) - Contains various optimized filtering algorithms to be used during calibration,
- [`plotting`](https://github.com/brianwelman2/kal-cal/tree/main/kalcal/plotting) - Set of plotting tools to look at results of the calibration,
- [`smoothers`](https://github.com/brianwelman2/kal-cal/tree/main/kalcal/smoothers) - Contains various optimized smoothing algorithms to be used during calibration,
- [`tools`](https://github.com/brianwelman2/kal-cal/tree/main/kalcal/tools) - Extra functionality and utilities too small for its own section,
- [`tuners`](https://github.com/brianwelman2/kal-cal/tree/main/kalcal/tuners) - Hyperparameter tuning algorithms based on EM-algorithm for linear Kalman filters and smoothers.

If you want to create data to test the library on, use the `create` section to generate a measurement set, gains to corrupt the visibilities, and then the visibilities corrupted by the gains with added noise. 

Next, utilize an algorithm from the `calibration` section to calibrate this newly simulated measurement set. Once complete, plot the results from the calibration using the `plotting` section.

For a quick tutorial, see the [API tutorial](https://github.com/brianwelman2/kal-cal/tree/main/kalcal/examples/api) and [CLI tutorial](https://github.com/brianwelman2/kal-cal/tree/main/kalcal/examples/cli) in `examples` section.

## Documentation
*TBD*

## CI
This library uses [github-actions](https://github.com/features/actions) for continuous integration tests on the same repository.

## License
This package uses the [MIT](https://choosealicense.com/licenses/mit/) license.