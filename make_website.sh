#!/bin/bash
jupyter nbconvert --to html --execute index.ipynb
jupyter nbconvert --to html --execute better_index.ipynb
rsync -ravz --delete *index.html hpc05@tnw-tn1.tudelft.net:
rm -f index.html better_index.html
