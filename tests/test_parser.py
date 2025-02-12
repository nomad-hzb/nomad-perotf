import os

import pytest
from nomad.client import normalize_all, parse


def set_monkey_patch(monkeypatch):
    def mockreturn_search(*args):
        return None

    monkeypatch.setattr(
        'nomad_perotf.parsers.perotf_measurement_parser.set_sample_reference',
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
        'UserGivenName_pX1_MPPT_lt_lp0_20250109T171021.mpp.txt',
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
