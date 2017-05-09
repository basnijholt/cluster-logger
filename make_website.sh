#!/bin/bash
jupyter nbconvert --to html --execute index.ipynb
rsync -ravz --delete index.html hpc05@tnw-tn1.tudelft.net:
