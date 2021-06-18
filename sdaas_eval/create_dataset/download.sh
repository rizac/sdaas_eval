SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
D_DIR="$SCRIPT_DIR/download_configs"

DBPATH=TMP=`python -c 'import os;from stream2segment.process import yaml_load;print(yaml_load("./dburl.private.yaml")["dburl"])'`

s2s download -d $DBPATH -c "$D_DIR"/europe_eida.yaml --minmagnitude 4 --start 1999-01-01T00:00:00
s2s download -d $DBPATH -c "$D_DIR"/chile_geofon.yaml --minmagnitude 4 --start 1999-01-01T00:00:00
s2s download -d $DBPATH -c "$D_DIR"/california_iris.yaml --minmagnitude 4 --start 1999-01-01T00:00:00

s2s download -d $DBPATH -c "$D_DIR"/europe_eida.yaml --minmagnitude 2.5 --maxmagnitude 4 --start 2020-06-01
s2s download -d $DBPATH -c "$D_DIR"/chile_geofon.yaml --minmagnitude 2.5 --maxmagnitude 4 --start 2020-06-01
s2s download -d $DBPATH -c "$D_DIR"/california_iris.yaml --minmagnitude 2.5 --maxmagnitude 4 --start 2020-06-01

# s2s download -d $DBPATH -c "$D_DIR"/europe_eida.yaml --minmagnitude 4 -w 2.1 "-0.1" --start 2020-01-01 "$ARGS"
# s2s download -d $DBPATH -c "$D_DIR"/chile_geofon.yaml --minmagnitude 4 -w 2.1 "-0.1" --start 2020-01-01 "$ARGS"
# s2s download -d $DBPATH -c "$D_DIR"/california_iris.yaml --minmagnitude 4 -w 2.1 "-0.1" --start 2020-01-01 "$ARGS"

