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
        # Parse header lines manually before using pandas
        header_dict = {}
        headerlines = 0
        lines = filedata.split('\n')
        
        for i, line in enumerate(lines):
            parts = line.split('\t')
            
            # Check if this is the data header line (starts with "Time Difference")
            if len(parts) > 0 and 'Time Difference' in parts[0]:
                headerlines = i
                break
            
            # Try to detect datetime (should be in row 1 or 2)
            # Look for a line that starts with a date pattern
            if i == 1 and len(parts) >= 2:
                # Try to parse as potential datetime
                try:
                    # Check if first part looks like a date
                    if '-' in parts[0] and ':' in parts[1]:
                        header_dict.update({'datetime': f'{parts[0]} {parts[1]}'})
                        continue
                except (IndexError, TypeError):
                    pass
            
            # Parse other metadata (key-value pairs where col1=key, col2=value)
            if len(parts) >= 2 and parts[0] and 'SPP measurement' not in parts[0] and 'Time Difference' not in parts[0]:
                key = str(parts[0]).lower().replace(' ', '_').replace('[', '').replace(']', '')
                try:
                    header_dict.update({key: float(parts[1])})
                except (ValueError, TypeError):
                    header_dict.update({key: str(parts[1])})

        # Read the actual data starting from the header line
        df = pd.read_csv(
            StringIO(filedata),
            skiprows=list(range(headerlines)) + [headerlines + 1],  # Skip metadata and units row
            sep='\t',
            header=0,  # First row after skiprows is the header
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