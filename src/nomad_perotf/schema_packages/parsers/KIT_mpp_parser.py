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
    elif '[Task information]' in file_content:
        return 'puri'
    elif 'SPP measurement' in file_content:
        return 'labview'
    else: # unrecognized file format
        raise TypeError("unrecognized file format")


def get_parameter(d, key):
    return d[key] if key in d else None


def parse_numeric_with_unit(value, default_unit=None):
    if value is None:
        return None
    if isinstance(value, (int, float, np.floating)):
        return float(value)
    text = str(value).strip()
    if not text:
        return None
    parts = text.split()
    try:
        number = float(parts[0])
    except ValueError:
        return None
    unit = parts[1].lower() if len(parts) > 1 else (default_unit or '').lower()
    if unit in {'mv'}:
        return number / 1000.0
    if unit in {'v', ''}:
        return number
    if unit in {'ms'}:
        return number / 1000.0
    if unit in {'s'}:
        return number
    return number


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

    elif file_type == 'puri':
        # Parse header lines with key: value format
        header_dict = {}
        
        lines = filedata.split('\n')
        for line in lines:
            line = line.strip()
            
            # Skip empty lines or section headers
            if not line or line == '#' or '[' in line:
                continue
            
            # Remove leading # and parse key: value pairs
            if line.startswith('#'):
                line = line[1:].strip()
            
            if ': ' in line:
                key, value = line.split(': ', 1)
                key = key.strip().lower().replace(' ', '_').replace('(', '').replace(')', '')
                value = value.strip()
                
                # Try to convert to float, otherwise keep as string
                try:
                    header_dict[key] = float(value)
                except ValueError:
                    header_dict[key] = value

        # Read CSV data lines, skipping comment metadata
        df = pd.read_csv(
            StringIO(filedata),
            sep=',',
            header=0,
            comment='#',
            engine='python',
            on_bad_lines='skip',
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

    elif file_type == 'puri':
        # Helper function to find column by partial match
        def get_column(df, key_patterns):
            for pattern in key_patterns if isinstance(key_patterns, list) else [key_patterns]:
                pattern_lower = pattern.lower()
                for col in df.columns:
                    if pattern_lower in str(col).lower():
                        return col
            return None

        def find_timestamp_column_by_value(df):
            for col in df.columns:
                series = pd.to_numeric(df[col], errors='coerce')
                sample = series.dropna().head(5)
                if sample.empty:
                    continue
                if (sample > 1e11).all():
                    return col
            return None

        def find_time_string_column(df):
            for col in df.columns:
                sample = df[col].astype(str).head(5)
                if sample.str.match(r'\d{4}-\d{2}-\d{2}').any():
                    return col
            return None
        
        # Find the timestamp column
        timestamp_col = get_column(df, ['timestamp', 'time'])
        if timestamp_col is None:
            timestamp_col = find_timestamp_column_by_value(df)
        if timestamp_col is None:
            raise ValueError(f"Timestamp column not found. Available columns: {df.columns.tolist()}")
        
        # Define first measurement as time difference 0 and calculate all diffs
        df['time_diff'] = pd.to_numeric(df[timestamp_col], errors='coerce') / 1000.0
        df['time_diff'] = df['time_diff'] - df['time_diff'].iloc[0]
        mpp_entitiy.time = np.array(df['time_diff'])
        
        # Find power column
        power_col = get_column(df, ['power', 'mw', 'mW'])
        if power_col is not None:
            mpp_entitiy.power_density = np.array(df[power_col])
        
        # Find voltage column
        voltage_col = get_column(df, ['voltage', 'v(v)', 'v'])
        if voltage_col is not None:
            mpp_entitiy.voltage = np.array(df[voltage_col])
        
        # Find current density column
        current_col = get_column(df, ['current', 'j(ma', 'ma/cm'])
        if current_col is not None:
            mpp_entitiy.current_density = np.array(df[current_col])
        
        # Find efficiency/PCE column
        efficiency_col = get_column(df, ['efficiency', 'pce', 'pce('])
        if efficiency_col is not None:
            mpp_entitiy.efficiency = np.array(df[efficiency_col])
        
        if mainfile is not None:
            mpp_entitiy.data_file = mainfile

        # datetime format: extract the first datetime value from the Time column
        try:
            time_col = get_column(df, ['time', 'datetime', 'date'])
            if time_col is None:
                time_col = find_time_string_column(df)
            if time_col is not None:
                first_datetime = df[time_col].iloc[0]
                mpp_entitiy.datetime = str(first_datetime)
        except (IndexError, KeyError, TypeError):
            pass
        
        properties = MPPTrackingProperties()
        
        # Set properties from header_dict
        properties.perturbation_frequency = parse_numeric_with_unit(
            get_parameter(header_dict, 'recorrd_period'), default_unit='s'
        )
        properties.perturbation_voltage = parse_numeric_with_unit(
            get_parameter(header_dict, 'step'), default_unit='v'
        )
        properties.perturbation_delay = parse_numeric_with_unit(
            get_parameter(header_dict, 'pertubation_period'), default_unit='s'
        )
        # Duration of measurement: last timestamp in seconds
        if len(df['time_diff']) > 0:
            properties.time = df['time_diff'].iloc[-1]
        
        if efficiency_col is not None and len(df[efficiency_col]) > 0:
            properties.last_pce = df[efficiency_col].iloc[-1]
        
        if voltage_col is not None and len(df[voltage_col]) > 0:
            properties.last_vmpp = df[voltage_col].iloc[-1]
        
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