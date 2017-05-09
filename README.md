Add this to `crontab -e`, make sure there is a newline on top of the file.
```
*/15 * * * * . ${HOME}/.bash_profile; ${HOME}/Work/cluster_log/run_logger.sh
```

Also make sure that `${HOME}/Work/cluster_log/run_logger.sh` runs without any issues before adding it to cron.