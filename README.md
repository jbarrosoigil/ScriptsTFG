# H1743-322 RXTE Analysis Pipeline

## Overview

This repository contains the Python scripts developed for the analysis of archival RXTE/PCA observations of the black-hole X-ray binary **H1743-322**.

The pipeline automates the preparation of RXTE observations, extraction of PCA spectra, computation of count rates and hardness ratios, generation of light curves and hardness–intensity diagrams, and the creation of a database of spectral-fit parameters for scientific analysis.

The code was developed as part of a Bachelor's Thesis focused on the spectral evolution of the 2003 outburst of H1743-322 and the investigation of a peculiar dip event during the soft state.

**Note:** The scripts were developed for a specific directory structure and RXTE data layout. Paths, folder names, and HEASOFT task parameters may need adaptation before use on a different dataset.

---

## Requirements

### Software

* HEASOFT / FTOOLS
* Python 3

### Python packages

* numpy
* pandas
* matplotlib
* astropy

---

## Directory Structure

The scripts must be executed from the directory containing the RXTE observation folders.

Example:

```text
project/
│
├── P80137/
├── P80138/
├── P90058/
├── ...
│
├── folders.py
├── goodTimeFilter.py
├── spectra.py
├── summation.py
├── lightCurve.py
├── MakeDDBB.py
└── GraphDDBB.py
```

Each observation directory is expected to contain the original RXTE data products.

---

## Workflow

The scripts should be executed in the following order.

### 1. Observation Preparation

```bash
python folders.py
```

Runs `pcaprepobsid` on all observation directories and creates the files required for subsequent RXTE reduction steps.

Output:

```text
<ObsID>-result/
```

containing filter files, event lists, and auxiliary products.

---

### 2. Good Time Interval Generation

```bash
python goodTimeFilter.py
```

Creates Good Time Interval (GTI) files using standard RXTE screening criteria:

* ELV > 4°
* OFFSET < 0.1°
* NUM_PCU_ON > 0

Output:

```text
<ObsID>-all-basic.gti
```

---

### 3. Spectral Extraction

```bash
python spectra.py
```

Extracts PCA source and background spectra using `pcaextspect2`.

Outputs:

```text
<ObsID>-all_src.pha
<ObsID>-all_bkg.pha
<ObsID>-all.rsp
```

---

### 4. Count Rate and Hardness Ratio Calculation

```bash
python summation.py
```

Computes:

* Net count rate
* Count-rate uncertainty
* Hardness ratio
* Hardness-ratio uncertainty
* Observation metadata

Output:

```text
<ObsID>.txt
```

for every observation.

---

### 5. Light Curves and Hardness–Intensity Diagrams

```bash
python lightCurve.py
```

Generates:

* Global light curves
* Individual outburst light curves
* Hardness–Intensity Diagrams (HIDs)
* Diagnostic plots for anomalous observations

Output directory:

```text
figures/
```

---

### 6. Spectral Fitting

Spectral fitting is performed externally using XSPEC.

The selected observations are fitted individually and the resulting parameters are stored as:

```text
<ObsID>_src.fitresults
```

These files contain quantities such as:

* Hydrogen column density (N_H)
* Photon index (Γ)
* Scattering fraction
* Disk temperature
* Disk normalization

---

### 7. Database Construction

```bash
python MakeDDBB.py
```

Combines timing information and spectral-fit results into a single database.

Output:

```text
results.csv
```

Columns include:

* Observation ID
* MJD
* Count rate
* Hardness ratio
* Exposure
* Background rate
* N_H
* Γ
* Scattering fraction
* Disk temperature
* Disk normalization

---

### 8. Scientific Plots

```bash
python GraphDDBB.py
```

Generates the final scientific figures used for analysis.

These include:

* Evolution of count rate
* Evolution of hardness ratio
* Disk temperature evolution
* Disk normalization evolution
* Photon index evolution
* Estimated inner disk radius evolution
* Correlation plots between spectral parameters

Outputs are stored in:

```text
figures/
```

---

## Scientific Context

The pipeline was developed to study the spectral and temporal evolution of H1743-322 during its RXTE-observed outbursts, with particular emphasis on the 2003 outburst.

The analysis combines timing and spectral information to investigate accretion-state transitions and the physical origin of an unusual dip observed during the soft state.

---

## Author

Joan Barroso i Gil
