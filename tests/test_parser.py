import os

import pytest
from nomad.client import normalize_all, parse

from nomad_perotf.schema_packages.perotf_package import (
    peroTF_CR_SolSimBox_JVmeasurement,
    peroTF_CR_SolSimBox_MPPTracking,
    peroTF_TFL_GammaBox_JVmeasurement,
)


def set_monkey_patch(monkeypatch):
    def mockreturn_search(*args):
        return None

    monkeypatch.setattr(
        'nomad_perotf.parsers.perotf_measurement_parser.set_sample_reference',
        mockreturn_search,
    )

    monkeypatch.setattr(
        'nomad_perotf.schema_packages.perotf_package.set_sample_reference',
        mockreturn_search,
    )


def delete_json():
    for file in os.listdir(os.path.join('tests/data')):
        if not file.endswith('archive.json'):
            continue
        os.remove(os.path.join('tests', 'data', file))


def get_archive(file_base, monkeypatch):
    set_monkey_patch(monkeypatch)
    file_name = os.path.join('tests', 'data', file_base)
    file_archive = parse(file_name)[0]
    assert file_archive.data

    for file in os.listdir(os.path.join('tests/data')):
        if 'archive.json' not in file:
            continue
        measurement = os.path.join('tests', 'data', file)
        measurement_archive = parse(measurement)[0]

    return measurement_archive


@pytest.fixture(
    params=[
        '20250114_experiment_file.xlsx',
        'KIT_DaBa_20230202_Batch-1_0_7.px7_mid.jv.csv',
        'UserGivenName_pX1_MPPT_lt_lp0_20250109T171021.mpp.txt',
        'UserGivenName_pX1_fwd_lt_lp0_20250109T164058.jv.txt',
        'KIT_DaBa_20230219_Experimnt-AB_2_2_MPP.1.mpp.csv',
        'AA00_C3_20.47mAcm-2.eqe.dat',
    ]
)
def parsed_archive(request, monkeypatch):
    """
    Sets up data for testing and cleans up after the test.
    """
    yield get_archive(request.param, monkeypatch)


def test_normalize_all(parsed_archive, monkeypatch):
    normalize_all(parsed_archive)
    delete_json()


def test_jv_files(monkeypatch):
    file = 'KIT_DaBa_20230202_Batch-1_0_7.px7_mid.jv.csv'
    archive = get_archive(file, monkeypatch)
    normalize_all(archive)

    assert archive.data
    assert archive.metadata.entry_type == 'peroTF_JVmeasurement'
    assert archive.data.multijunction_position == 'mid'
    assert archive.data.measurement_programm == 'labview'

    archive.data = peroTF_CR_SolSimBox_JVmeasurement()
    archive.data.data_file = file
    archive.metadata.entry_type = None
    normalize_all(archive)

    assert archive.data
    assert archive.metadata.entry_type == 'peroTF_CR_SolSimBox_JVmeasurement'

    archive.data = peroTF_TFL_GammaBox_JVmeasurement()
    archive.data.data_file = file
    archive.metadata.entry_type = None
    normalize_all(archive)

    assert archive.data
    assert archive.metadata.entry_type == 'peroTF_TFL_GammaBox_JVmeasurement'

    delete_json()


def test_mpp_files(monkeypatch):
    file = 'KIT_DaBa_20230219_Experimnt-AB_2_2_MPP.1.mpp.csv'
    archive = get_archive(file, monkeypatch)
    normalize_all(archive)

    assert archive.data
    assert archive.metadata.entry_type == 'peroTF_MPPTracking'
    assert archive.data.measurement_programm == 'labview'

    archive.data = peroTF_CR_SolSimBox_MPPTracking()
    archive.data.data_file = file
    archive.metadata.entry_type = None
    normalize_all(archive)

    assert archive.data
    assert archive.metadata.entry_type == 'peroTF_CR_SolSimBox_MPPTracking'

    delete_json()
