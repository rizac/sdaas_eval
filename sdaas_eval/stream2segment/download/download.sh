SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

DBPATH="postgresql://me:***@localhost/accelerometers"
# DBPATH="sqlite:///${SCRIPT_DIR}/accelerometers.sqlite"
ARGS=""  #  "--print-config-only"

s2s download -d $DBPATH -c "$SCRIPT_DIR"/europe_eida.yaml --minmagnitude 4 --start 1999-01-01T00:00:00
s2s download -d $DBPATH -c "$SCRIPT_DIR"/chile_geofon.yaml --minmagnitude 4 --start 1999-01-01T00:00:00
s2s download -d $DBPATH -c "$SCRIPT_DIR"/california_iris.yaml --minmagnitude 4 --start 1999-01-01T00:00:00

s2s download -d $DBPATH -c "$SCRIPT_DIR"/europe_eida.yaml --minmagnitude 2.5 --maxmagnitude 4 --start 2020-06-01
s2s download -d $DBPATH -c "$SCRIPT_DIR"/chile_geofon.yaml --minmagnitude 2.5 --maxmagnitude 4 --start 2020-06-01
s2s download -d $DBPATH -c "$SCRIPT_DIR"/california_iris.yaml --minmagnitude 2.5 --maxmagnitude 4 --start 2020-06-01

# s2s download -d $DBPATH -c "$SCRIPT_DIR"/europe_eida.yaml --minmagnitude 4 -w 2.1 "-0.1" --start 2020-01-01 "$ARGS"
# s2s download -d $DBPATH -c "$SCRIPT_DIR"/chile_geofon.yaml --minmagnitude 4 -w 2.1 "-0.1" --start 2020-01-01 "$ARGS"
# s2s download -d $DBPATH -c "$SCRIPT_DIR"/california_iris.yaml --minmagnitude 4 -w 2.1 "-0.1" --start 2020-01-01 "$ARGS"

