
import sys
import yaml
import re
import datetime as DT

import logging
from rainbow_logging_handler import RainbowLoggingHandler

import pandas as pd
import numpy as np
from sklearn import preprocessing
from sklearn_pandas import DataFrameMapper

# Capturing current module. Needed to call getattr on this module
this_module = sys.modules[__name__]

# Setup logging module
# TODO: Figure out a standard way to install/handle logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(filename)s:%(lineno)4s - %(funcName)15s()] %(levelname)8s: %(message)s')

# Setup RainbowLoggingHandler
handler = RainbowLoggingHandler(sys.stderr, color_funcName=('black', 'yellow', True))
handler.setFormatter(formatter)
logger.addHandler(handler)

# Converting Boolean to String during YAML load
# Done to workaround quirkness with PyYAML

def bool_constructor(self, node):
    value = self.construct_yaml_bool(node)
    if value == False:
        return 'False'
    else:
        return 'True'
yaml.Loader.add_constructor(u'tag:yaml.org,2002:bool', bool_constructor)
yaml.SafeLoader.add_constructor(u'tag:yaml.org,2002:bool', bool_constructor)

# Load data from CSV, configuration file
# Process data and provide input/output data frames

def load_data(data_csv, data_cfg):

    # Load Data YAML configuration file
    with open(data_cfg, 'r') as yf:
        data = yaml.load(yf)

    # Read CSV into data frame
    df = pd.read_csv(data_csv)
    # Filling holes with zeros
    df.fillna(0, inplace=True)

    # Process Columns
    for item in data:
        if item['include'] == False:
            continue
        else:
            colnum = item['column']
            logger.info('Processing Column %s', colnum)

            # Create a column data frame
            col_df = df.iloc[:, [colnum-1]].copy()
            logger.debug(col_df.columns)
            logger.debug('Preprocess Column Input\n%s', col_df.head())

            # Apply transformations
            col_df = do_transform(col_df, item['transform'])
            logger.debug('Preprocess Column Output\n%s', col_df.head())

# Perform Data Transformations
def do_transform(df, tf):
    for func in tf:
        funckey, funcval = func.items()[0]

        # Getting transformation call name
        transform = getattr(this_module, funckey, None)

        # Splitting funcval to individual function arguments
        # First argument is True/False to indicate if transform is called
        try:
            pattern = re.compile('\s*,\s*')
            funcvals = pattern.split(funcval)
            logger.debug('Funcvals --> %s', funcvals)
        except AttributeError:
            funcvals = [funcval]

        # Calling transformation
        if funcvals[0] == 'True':
            try:
                logger.debug('Funckey --> %s', funckey)
                df = transform(df, funcvals[1:])
            except AttributeError:
                logger.error('Function %s has not been implemented!', funckey)
    return df

# Performs feature scaling on data frame
# TODO: scale - Add implementation to handle val
def scale(df, val):
    logger.info('Function %s called..', sys._getframe().f_code.co_name)
    mms = preprocessing.MinMaxScaler()
    return pd.DataFrame(mms.fit_transform(df.values.ravel().reshape(-1, 1)), columns=df.columns)

# conv2num: Converts column data to ordered integers
# TODO: conv2num - Add implementation to handle args
def conv2num(df, args):
    logger.info('Function %s called..', sys._getframe().f_code.co_name)
    le = preprocessing.LabelEncoder()
    return pd.DataFrame(le.fit_transform(df.values.ravel()), columns=df.columns)

# conv2bin: Converts column data to binary
# TODO: conv2bin - Add implementation to handle args
def conv2bin(df, args):
    logger.info('Function %s called..', sys._getframe().f_code.co_name)
    le = preprocessing.LabelBinarizer()
    return pd.DataFrame(le.fit_transform(df.values.ravel()), columns=df.columns)

# conv2timedelta: Converts column data to age
# TODO: conv2timedelta - Current returns in years. May need to make it more scalable
def conv2timedelta(df, args):
    logger.info('Function %s called..', sys._getframe().f_code.co_name)
    if args[1] == 'now':
        refdate = pd.Timestamp(DT.datetime.now())
    else:
        refdate = pd.Timestamp(DT.datetime.strptime(args[1], args[0]))
    logger.debug('Reference date is: %s', refdate)
    df = pd.DataFrame((refdate - pd.to_datetime(df.values.ravel())), columns=df.columns)
    return df.apply(lambda x: (x/np.timedelta64(1, 'Y')).astype(int))

# Main Program
if __name__ == '__main__':
    load_data('nflData.csv', 'datacfg.yaml')
