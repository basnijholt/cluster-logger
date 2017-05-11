#!/bin/bash
python logger.py >> error.log 2>&1
python better_logger.py >> better_error.log 2>&1
