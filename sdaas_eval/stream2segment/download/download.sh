DBPATH="postgresql://me:***@localhost/accelerometers"

s2s download -d $DBPATH -c ./europe_eida --minmagnitude 4 --start 1999-01-01T00:00:00
s2s download -d $DBPATH -c ./chile_geofon --minmagnitude 4 --start 1999-01-01T00:00:00
s2s download -d $DBPATH -c ./california_iris --minmagnitude 4 --start 1999-01-01T00:00:00

s2s download -d $DBPATH -c ./europe_eida --minmagnitude 2.5 --maxmagnitude 4 --start 365
s2s download -d $DBPATH -c ./chile_geofon --minmagnitude 2.5 --maxmagnitude 4 --start 365
s2s download -d $DBPATH -c ./california_iris --minmagnitude 2.5 --maxmagnitude 4 --start 365

s2s download -d $DBPATH -c ./europe_eida --minmagnitude 4 -w 2.1 "-0.1" --start 365
s2s download -d $DBPATH -c ./chile_geofon --minmagnitude 4 -w 2.1 "-0.1" --start 365
s2s download -d $DBPATH -c ./california_iris --minmagnitude 4 -w 2.1 "-0.1" --start 365

