import io
import re
import zipfile
from pathlib import Path

import pandas as pd

from baseclasses.characterizations import XRDData


def parse_xy_data(file_content):
    if isinstance(file_content, (bytes, bytearray)):
        text = file_content.decode('utf-8', errors='replace')
    else:
        text = str(file_content)

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        raise ValueError('No XY data found in file.')

    skiprows = 1 if lines and 'Id' in lines[0] else 0
    sample_line = lines[skiprows] if skiprows < len(lines) else lines[0]
    decimal = ',' if ',' in sample_line else '.'

    data = pd.read_csv(
        io.StringIO(text),
        sep=r' |\t',
        decimal=decimal,
        header=None,
        skiprows=skiprows,
        engine='python',
    )
    data = data.dropna(subset=[0, 1])
    data[0] = pd.to_numeric(data[0], errors='coerce')
    data[1] = pd.to_numeric(data[1], errors='coerce')
    data = data.dropna(subset=[0, 1])

    if data.empty:
        raise ValueError('No valid XY data points found.')

    return XRDData(angle=data[0].to_numpy(), intensity=data[1].to_numpy())


def parse_brml_data(file_content):
    if isinstance(file_content, (str, Path)):
        with open(file_content, 'rb') as f:
            data = f.read()
    elif isinstance(file_content, (bytes, bytearray)):
        data = bytes(file_content)
    else:
        raise TypeError('BRML data must be bytes, a path, or a file-like object.')

    try:
        with zipfile.ZipFile(io.BytesIO(data), 'r') as brml:
            rawdata_files = [
                name
                for name in brml.namelist()
                if re.match(r'Experiment\d+/RawData\d+\.xml$', name)
            ]
            if not rawdata_files:
                raise RuntimeError('No RawData*.xml found in BRML file.')

            data_points = []
            for rawdata_file in rawdata_files:
                xml = brml.read(rawdata_file).decode('utf-8', errors='replace')
                for datum in re.findall(r'<Datum>(.*?)</Datum>', xml, flags=re.DOTALL):
                    values = [entry.strip() for entry in datum.split(',')]
                    if len(values) < 5:
                        continue
                    try:
                        two_theta = float(values[2])
                        intensity = float(values[4])
                    except ValueError:
                        continue
                    data_points.append((two_theta, intensity))
    except zipfile.BadZipFile as exc:
        raise ValueError('Invalid BRML ZIP file content.') from exc

    if not data_points:
        raise RuntimeError('No valid XRD data points found in BRML file.')

    angle = [point[0] for point in data_points]
    intensity = [point[1] for point in data_points]
    return XRDData(angle=angle, intensity=intensity)


def parse_xrd_data(file_content, filename=''):
    suffix = str(filename).lower()
    if suffix.endswith('.brml'):
        return parse_brml_data(file_content)
    if suffix.endswith('.xy'):
        return parse_xy_data(file_content)
    if isinstance(file_content, (bytes, bytearray)):
        try:
            return parse_brml_data(file_content)
        except (RuntimeError, ValueError):
            return parse_xy_data(file_content)
    return parse_xy_data(file_content)
