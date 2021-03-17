# sdaas_eval

Package for evaluating data of the `sdaas` project. New branch of the old `sod` package

A machine learning experimental project to detect seismic events outliers

The Package ROOT dir is the one in which you clone this package (usually called 'sdaas_eval'.
Therein you will have a nested 'sdaas_eval' directory with the python code, 
and a 'test' directory where tests are implemented, plus other files, e.g. `requirements.txt`)


# dataset creation

A dataset is a dataframe (HDF file) with input data for training
and creating a classifier (or testing and already created classifier).
To create a new dataset with name <dataset>:

1. Implement <dataset>.yaml and <dataset>.py in sdaas_eval/stream2segment/configs
   (for info, see stream2segment documentation)

2. Move to ROOT
   Activate virtualenv
   With a given input database path, execute:
   ```bash
   s2s process -d postgresql://<user>:<pwsd>@<host>/<dbname> -mp -c ./sdaas_eval/stream2segment/configs/<dataset>.yaml -p ./sdaas_eval/stream2segment/configs/<dataset>.py ./sdaas_eval/datasets/<dataset>.hdf
   ```

A new <dataset>.hdf file is created.


# copy files from different repos:

.model and .hdf files are ignored in git because too big in size, so you will need to copy them
with rsync or scp in case, e.g.:

Move locally to ROOT
(with <ROOT>, we denote the ROOT directory on the remote computer). Then:

rsync -auv <user>@<host>:<ROOT>/sdaas_eval/datasets/<dataset>.hdf ./sdaas_eval/datasets/
scp <user>@<host>:<ROOT>/sdaas_eval/datasets/<dataset>.hdf ./sdaas_eval/datasets/


# Evaluation results:

Evaluate means: iterate over a set of user defined hyperparameters (HP)
to create classifier(s) and evaluate them against a provided test set
producing a so-called Prediction dataframe saved in HDF format.
Already existing classifiers will not be created, already existing predictions will
not be overwritten.

You first need to configure your run by implementing a config file (in sdaas_eval/evaluations/configs) whose
name by convention starts with "eval." followed by any useful information, e.g. ususally
the dataset file NAME(s) used (e.g., "eval.allset_train_test.iforest.yaml").

*Important*: The config file name should be unique for each run: *NEW RUN => NEW CONFIG*.

Then move to ROOT, activate virtualenv and run:
```bash
export PYTHONPATH='.' && python sdaas_eval/evaluate.py -c "<yamlfilename>"
```

Results are saved in the directory '/sdaas_eval/evaluations/results':
- N model file (classifiers, one for each parameters set)
- N directories with same name as the classifier (excluding the classifier file extension,
  currently 'sklmodel') where the prediction dataframe is saved with the same testset name

*Important* file names are quite long as they are created with all hyperparameters and
informations available in a URL query string fashion (param1=value&param2=value...)

A summary evaluation HDF is also stored in '/sdaas_eval/evaluations/results' and will
consist of one row per evaluation, with some metrics.

# Jupyter

move to the jupyter sub-directory, run `jupyter notebook` and inspect/create new
Notebook for exploring the evluations and plotting results

<!--
# Clf evaluation

Evaluate a classifier means: iterate over a set of already created classifiers (HP) and
evaluate them against a provided test set.

You first need to configure your run by implementing a config file (in sdaas_eval/evaluations/configs) whose
name by convention starts with "clfeval." followed by any useful information e.g.,
the config file name of the evaluation used (see above) for creating the classifiers
(e.g. "clfeval.allset_train_test.iforest.psd@5sec.yaml").

*Important*: The config file name should be unique for each run: *NEW RUN => NEW CONFIG*.

Then proceed as for Evaluation, see above (the only thing that changes is the config file name.
Internally, the program recognizes automatically from the config content if it has to run an
Evaluation or a Clf evaluation)

Results are saved in the directory '/sdaas_eval/evaluation/<configfilename>':
- N prediction files (hdf files with the predictions of all elements in the input dataset)
- one HTML report with % recognized and log loss (sort of)

-->