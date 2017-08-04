#!/bin/bash
jupyter nbconvert --to html --execute --ExecutePreprocessor.timeout=600 --log-level WARN index.ipynb >> error.log 2>&1
rsync -e "ssh -i $HOME/.ssh/id_rsa_hpc05.pub" -ravz index.html hpc05@tnw-tn1.tudelft.net:
rsync -e "ssh -i $HOME/.ssh/id_rsa_hpc05.pub" -ravz database.p hpc05@tnw-tn1.tudelft.net:
rm -f index.html
