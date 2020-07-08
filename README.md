# Algal Bloom Detection and Severity Quantification
A Python program that detects any possible algae present in an image and then quantifies and visualizes its severity.

## What is it?
An application written using the Python programming language that, as its name suggests, detects algal bloom present in an image. It then quantifies the algal bloom's severity, using several vegetation/biomass indices on a per-pixel basis, and then applies a gradient on the image that represents the calculated severity.

## How does it work?
This program utilizes three vegetation/biomass indices in order to quantify an algal bloom's severity, namely, the Normalized Red Green Difference Index (NGRDI), the Hue Index, and the Saturation Index. The latter two indices were based on the methodology used in the study by Park et al. (2019) titled "Single Image Based Algal Bloom Detection Using Water Body Extraction and Probabilistic Algae Indices". The value of each index for each pixel (that is considered to be algae by the program) is computed and then the final index named the Algal Bloom Detection Index is then computed by combining the previous indices by multiplying each of their values. [TODO: Extend this]
