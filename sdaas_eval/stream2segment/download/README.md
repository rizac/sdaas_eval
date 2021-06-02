Useful links:

- https://ds.iris.edu/ds/nodes/dmc/tutorials/waveforms-and-their-power-spectral-density-expressions/
- https://gfzpublic.gfz-potsdam.de/rest/items/item_4015_7/component/file_4016/content (Fig. 3.5 on page 8)
- https://ds.iris.edu/ds/nodes/dmc/data/formats/seed-channel-naming/

Download config from existing databases:
```bash
s2s dl config -d postgresql://${user}:${pswd}@${hname}.${hurl}/${dbname} -did ${did} ./sdaas_eval/stream2segment/download/sources/${hname}_${dbname}_did${did}.yaml
```
where

 - ${user} = r***
 - ${pswd} = E***
 - ${hname} = r***5
 - ${hurl} = g***.de
 - ${did} = download id (integer)
 

<!-- split training in [0-80] [80-200] [200+] -->
 