Add this to `crontab -e`, make sure there is a newline on top of the file.
```
*/15 * * * * $HOME/Work/cluster_log/cronjob.sh
30 23 * * * $HOME/Work/cluster_log/cronjob_clean.sh
```

Also make sure that `${HOME}/Work/cluster_log/cronjob.sh` runs without any issues before adding it to cron.
