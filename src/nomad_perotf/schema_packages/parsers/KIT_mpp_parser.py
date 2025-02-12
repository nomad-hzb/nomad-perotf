from datetime import datetime
from io import StringIO

import numpy as np
import pandas as pd

# import glob
from baseclasses.solar_energy.mpp_tracking import MPPTrackingProperties


def identify_file_type(file_content):
    """
    Identify whether the file is from LabVIEW or Python by checking for
    specific keywords.
    """
    if 'Singapore Solar Simulator, Python' in file_content:
        return 'python'
    return 'labview'


def get_parameter(d, key):
    return d[key] if key in d else None


def get_mpp_data(filedata):
    file_type = identify_file_type(filedata)

    if file_type == 'labview':
        df = pd.read_csv(
            StringIO(filedata),
            skiprows=0,
            sep='\t',
            # index_col=0,
            engine='python',
        )
        header_dict = {}
        for i, row in df.iterrows():
            if 'Time Difference' in row[0]:
                headerlines = i
                break

            if i == 0:
                header_dict.update({'datetime': f'{row[0]} {row[1]}'})
                continue
            key = row[0].lower().replace(' ', '_')
            try:
                header_dict.update({key: float(row[1])})
            except BaseException:
                header_dict.update({key: row[1]})

        df = pd.read_csv(
            StringIO(filedata),
            skiprows=range(headerlines + 2, headerlines + 3),
            sep='\t',
            header=headerlines + 1,
        )

    elif file_type == 'python':
        df = pd.read_csv(
            StringIO(filedata),
            skiprows=2,
            header=None,
            sep=':\t',
            nrows=25,
            # index_col=0,
            engine='python',
        )
        header_dict = {}
        for i, row in df.iterrows():
            if i == 0:
                header_dict.update({'datetime': f'{row[1]}'})
                continue
            key = row[0].lower().replace(' ', '_')
            try:
                header_dict.update({key: float(row[1])})
            except BaseException:
                header_dict.update({key: row[1]})

        df = pd.read_csv(
            StringIO(filedata),
            skiprows=29,
            sep='\t',
        )

    return header_dict, df, file_type


def get_mpp_archive(header_dict, file_type, df, mpp_entitiy, mainfile=None):
    if file_type == 'labview':
        mpp_entitiy.time = np.array(df['Time Difference'])
        mpp_entitiy.power_density = np.array(df['Power'])
        mpp_entitiy.voltage = np.array(df['Voltage'])
        mpp_entitiy.current_density = np.array(df['Current Density'])
        mpp_entitiy.efficiency = np.array(df['PCE'])
        if mainfile is not None:
            mpp_entitiy.data_file = mainfile

        datetime_str = get_parameter(header_dict, 'datetime')
        datetime_object = datetime.strptime(datetime_str, '%Y-%m-%d %I:%M %p')
        mpp_entitiy.datetime = datetime_object.strftime('%Y-%m-%d %H:%M:%S.%f')

        properties = MPPTrackingProperties()
        properties.start_voltage_manually = (
            get_parameter(header_dict, 'start_voltage_manually') == 'true'
        )
        properties.perturbation_frequency = get_parameter(
            header_dict, 'perturbation_frequency_[s]'
        )
        properties.sampling = get_parameter(header_dict, 'sampling')
        properties.perturbation_voltage = get_parameter(
            header_dict, 'perturbation_voltage_[v]'
        )
        properties.perturbation_delay = get_parameter(
            header_dict, 'perturbation_delay_[s]'
        )
        properties.time = get_parameter(header_dict, 'time_[s]')
        properties.status = get_parameter(header_dict, 'status')
        properties.last_pce = get_parameter(header_dict, 'last_pce_[%]')
        properties.last_vmpp = get_parameter(header_dict, 'last_vmpp_[v]')

        mpp_entitiy.properties = properties

    elif file_type == 'python':
        mpp_entitiy.time = np.array(df['Time'])
        mpp_entitiy.power_density = np.array(df['Power'])
        mpp_entitiy.voltage = np.array(df['Voltage'])
        mpp_entitiy.current_density = np.array(df['CurrentDensity'])
        # mpp_entitiy.efficiency = np.array(df['PCE'])
        if mainfile is not None:
            mpp_entitiy.data_file = mainfile

        datetime_str = get_parameter(header_dict, 'datetime')
        datetime_object = datetime.strptime(datetime_str, '%a %b %d %H:%M:%S %Y')
        mpp_entitiy.datetime = datetime_object.strftime('%Y-%m-%d %H:%M:%S.%f')

        properties = MPPTrackingProperties()

        mpp_entitiy.properties = properties


# with open(
#     '/home/a2853/Downloads/UserGivenName_pX1_MPPT_lt_lp0_20250109T171021.mpp.txt'
# ) as f:
#     get_mpp_data(f.read())
