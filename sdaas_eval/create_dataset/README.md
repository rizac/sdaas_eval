# Stream23segment directory (download, feature extraction, GUI)

Copy `dburl.yaml` into `dburl.private.yaml`
(git ignored, you can safely type sensitive information)
and setup the database URL therein.

Then:

## Download

```bash
./download.sh
```

To add new configs:
 - add a new YAMl config in `download_configs`.
   If the config is modified from a previous download
   you can put the original unmodified config
   `download_configs/original_configs`
   (with name `<database>_<hostname>_did<download_id>.yaml`
   to keep track of the origin).
   
 - Edit `download.sh` accordingly

## Process / Feature extraction

`python ./features_extractor.py`

(creates a hdf file in this directory)


## GUI / Visualization

`python runguy.private.py`
