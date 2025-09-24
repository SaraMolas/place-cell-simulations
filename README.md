# Place cell simulation

This repository explores different methods for generating **synthetic place cell data**, focusing on modeling spatial fields in a 1D linear track environment.  

Currently, it contains two Jupyter notebooks:

1. **RatInABox_exploration.ipynb**  
   Uses the [RatInABox](https://github.com/RatInABox-Lab/RatInABox) package to generate synthetic place cells.  
   While testing, I found a bug in how place cells are created in a 1D linear track setup, which motivated further work.  

2. **linear_track_simulation.ipynb**  
   My own implementation of a place cell simulation in a 1D linear track.  
   This notebook currently simulates **two place cells** with Gaussian receptive fields centered at different positions.  

---

## Motivation

Place cells, discovered in the hippocampus, are neurons that fire when an animal is in a specific location in an environment.  
Modeling them synthetically is useful for:
- Testing spatial coding algorithms
- Validating analysis pipelines


---

## Getting Started

Clone the repo and install dependencies:

```bash
git clone https://github.com/SaraMolas/place-cell-simulations.git
cd place-cell-simulations
pip install -r requirements.txt
```

## Citations 

DOI: 10.5281/zenodo.17196242
