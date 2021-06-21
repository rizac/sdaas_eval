from stream2segment.process import yaml_load
from stream2segment.process.gui.main import show_gui
import os

thisdir = os.path.dirname(__file__)

dburl = yaml_load(os.path.join(thisdir, 'dburl.private.yaml'))['dburl']
c = '%s/features_extractor.yaml' % thisdir
p = '%s/features_extractor.py' % thisdir

show_gui(dburl, p, c)