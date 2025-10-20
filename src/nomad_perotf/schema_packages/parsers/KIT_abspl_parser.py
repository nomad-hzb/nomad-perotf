from io import StringIO

import pandas as pd

header_map_settings = {
    'Laser intensity (suns)': 'laser_intensity_suns',
    'Bias Voltage (V)': 'bias_voltage',
    'Bias voltage (V)': 'bias_voltage',
    'SMU current density (mA/cm2)': 'smu_current_density',
    'Integration Time (ms)': 'integration_time',
    'Delay time (s)': 'delay_time',
    'Delay Time (s)': 'delay_time',
    'EQE @ laser wavelength': 'eqe_laser_wavelength',
    'Laser spot size (cm²)': 'laser_spot_size',
    'Laser spot size (cm�)': 'laser_spot_size',
    'Subcell area (cm²)': 'subcell_area',
    'Subcell area (cm�)': 'subcell_area',
    'Subcell': 'subcell_description',
}
header_map_result = {
    'LuQY (%)': 'luminescence_quantum_yield',
    'QFLS (eV)': 'quasi_fermi_level_splitting',
    'QFLS LuQY (eV)': 'quasi_fermi_level_splitting',
    'QFLS HET (eV)': 'quasi_fermi_level_splitting_het',
    'iVoc (V) HET': 'quasi_fermi_level_splitting_het',
    'iVoc (V)': 'i_voc',
    'Bandgap (eV)': 'bandgap',
    'Jsc (mA/cm2)': 'derived_jsc',
}


def parse_abspl_data(data_file, archive, logger):
    """Parses the AbsPL data file and returns extracted settings and spectral arrays."""
    with archive.m_context.raw_file(data_file, mode='rb') as f:
        raw_bytes = f.read()
    text = raw_bytes.decode('cp1252', errors='replace')
    lines = text.splitlines()
    logger.debug('Read data file lines', file=data_file, total_lines=len(lines))

    settings_vals, result_vals, data_start_idx = parse_header(lines, logger)
    wavelengths, lum_flux, raw_counts, dark_counts = parse_numeric_data(
        lines, data_start_idx, logger
    )

    return settings_vals, result_vals, wavelengths, lum_flux, raw_counts, dark_counts


def parse_header(lines, logger):
    settings_vals = {}
    result_vals = {}
    header_done = False
    data_start_idx = None

    for idx, line in enumerate(lines):
        line_stripped = line.strip()
        if line_stripped.startswith('---'):
            data_start_idx = idx + 2  # skip dashed line and header line
            header_done = True
            break
        if '\t' in line:
            parts = line.split('\t', 1)
            if len(parts) == 2:  # noqa: PLR2004
                key = parts[0].strip()
                val_str = parts[1].strip()
                if key in header_map_settings:
                    if key == 'Subcell':
                        settings_vals[header_map_settings[key]] = val_str
                    else:
                        try:
                            settings_vals[header_map_settings[key]] = float(val_str)
                        except ValueError:
                            logger.debug(
                                'Could not convert header to float',
                                key=key,
                                val=val_str,
                            )
                elif key in header_map_result:
                    try:
                        result_vals[header_map_result[key]] = float(val_str)
                    except ValueError:
                        logger.debug(
                            'Could not convert result to float', key=key, val=val_str
                        )

    logger.debug('Header parsed', header_done=header_done, data_start=data_start_idx)
    return settings_vals, result_vals, data_start_idx


def parse_numeric_data(lines, data_start_idx, logger):
    wavelengths = []
    lum_flux = []
    raw_counts = []
    dark_counts = []

    if data_start_idx is not None and data_start_idx < len(lines):
        # Combine the remaining lines into a single string
        data_str = '\n'.join(lines[data_start_idx:])
        try:
            # Use pandas to read the data with flexible whitespace separation
            df = pd.read_csv(StringIO(data_str), delim_whitespace=True, header=None)

            if len(df.columns) >= 3:  # We need at least 3 columns
                wavelengths = df[0].tolist()
                lum_flux = df[1].tolist()
                raw_counts = df[2].tolist()
                if len(df.columns) > 3:  # If we have dark counts
                    dark_counts = df[3].tolist()
        except Exception as e:
            logger.debug('Could not parse numeric data with pandas', error=str(e))

    logger.debug(
        'Parsed numeric data',
        w_count=len(wavelengths),
        lf_count=len(lum_flux),
        rc_count=len(raw_counts),
        dc_count=len(dark_counts),
    )

    return wavelengths, lum_flux, raw_counts, dark_counts


def parse_multiple_abspl(filedata):
    metadata_str, data_str = filedata.split('----------------------------', 1)
    metadata = pd.read_csv(
        StringIO(metadata_str.strip()), sep='\t', header=None, index_col=0
    )
    data = pd.read_csv(StringIO(data_str.strip()), sep='\t', header=None, skiprows=2)

    settings_vals = {}
    results = {}
    for key in metadata.index:
        if key in header_map_settings:
            settings_vals[header_map_settings[key]] = metadata.loc[key][1]
        if key in header_map_result:
            results[header_map_result[key]] = metadata.loc[key]

    return settings_vals, results, data
