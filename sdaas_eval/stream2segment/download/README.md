Downloaded databases:

s2s dl config -d postgresql://rizac:***@rs5.gfz-potsdam.de/s2s_2020_05 -did 47 > ./sdaas_eval/stream2segment/download/s2s_2020_05.yaml
s2s dl config -d postgresql://rizac:***@rs5.gfz-potsdam.de/california2 -did 8 > ./sdaas_eval/stream2segment/download/iris.yaml
s2s dl config -d postgresql://rizac:***@rs5.gfz-potsdam.de/sod_chile -did 1 > ./sdaas_eval/stream2segment/download/sod_chile_id1.yaml

ALL:
 - check minsamplerate, depths
 - HL? is accelerometer?

CALIFORNIA: 
 - ndec o sdec?
 - latlng bounds are not too strict?