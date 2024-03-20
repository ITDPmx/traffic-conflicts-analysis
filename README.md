# traffic-conflicts-analysis

This repository aims to develop a methodology to clean the PIMUS network model for the GTAModel.

## Overall methodology

![methology](imgs/pipeline.jpg)

## Run locally with Nvidia GPU

Create RAPIDS environment
```bash
conda env create -f environment.yml
```
Activate environment
```bash
conda activate rapids
```


## References

Huge shoutout goes to RafalKucharskiPK for creating the net to csv converter.

 - [visum_to_pandas](https://github.com/RafalKucharskiPK/visum_to_pandas.git)
