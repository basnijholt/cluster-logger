#!/bin/bash
jupyter nbconvert --to html --execute --ExecutePreprocessor.timeout=3000 --log-level WARN index.ipynb >> error.log 2>&1
rsync -ravz index.html hpc05@tnw-tn1.tudelft.net:
rsync -ravz database.p hpc05@tnw-tn1.tudelft.net:
rm -f index.html
