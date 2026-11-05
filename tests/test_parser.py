import datetime
import os

import nomad
import pandas as pd
import pytest
from nomad.client import normalize_all, parse

from nomad_perotf.parsers.perotf_batch_parser import drop_text_in_unit_columns
from nomad_perotf.schema_packages.perotf_package import (
    peroTF_CR_SolSimBox_JVmeasurement,
    peroTF_CR_SolSimBox_MPPTracking,
    peroTF_TFL_GammaBox_JVmeasurement,
)


class A:
    def __init__(self):
        pass

    def raw_directory_list(self):
        return [F(p) for p in os.listdir(os.path.join('tests', 'data'))]


class F:
    def __init__(self, path):
        self.path = path


def set_monkey_patch(monkeypatch):
    def mockreturn_search(*args, **kwargs):
        return None

    monkeypatch.setattr(
        'nomad_perotf.parsers.perotf_measurement_parser.set_sample_reference',
        mockreturn_search,
    )

    monkeypatch.setattr(
        'nomad_perotf.schema_packages.perotf_package.set_sample_reference',
        mockreturn_search,
    )

    monkeypatch.setattr(
        nomad.datamodel.ServerContext,
        'upload_files',
        A(),
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
    # the new GUI shows only figures, not the a_plot annotation
    assert [f.label for f in archive.data.figures] == ['JV curves']

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


def test_jv_files_2(monkeypatch):
    file = 'UserGivenName_pX1_fwd_lt_lp0_20250109T164058.jv.txt'
    archive = get_archive(file, monkeypatch)
    c_context = archive.m_context
    archive.m_context = nomad.datamodel.ServerContext()
    archive.m_context.raw_file = c_context.raw_file
    normalize_all(archive)

    assert archive.data
    assert len(archive.data.jv_curve) == 2
    assert len(archive.data.figures[0].figure['data']) == 2
    delete_json()


def test_mpp_files(monkeypatch):
    file = 'KIT_DaBa_20230219_Experimnt-AB_2_2_MPP.1.mpp.csv'
    archive = get_archive(file, monkeypatch)
    normalize_all(archive)

    assert archive.data
    assert archive.metadata.entry_type == 'peroTF_MPPTracking'
    assert archive.data.measurement_programm == 'labview'
    assert [f.label for f in archive.data.figures] == ['MPP tracking']

    archive.data = peroTF_CR_SolSimBox_MPPTracking()
    archive.data.data_file = file
    archive.metadata.entry_type = None
    normalize_all(archive)

    assert archive.data
    assert archive.metadata.entry_type == 'peroTF_CR_SolSimBox_MPPTracking'

    delete_json()


def test_eqe_files(monkeypatch):
    archive = get_archive('AA00_C3_20.47mAcm-2.eqe.dat', monkeypatch)
    normalize_all(archive)

    assert archive.metadata.entry_type == 'peroTF_TFL_GammaBox_EQEmeasurement'
    assert [f.label for f in archive.data.figures] == ['EQE']
    delete_json()


def test_uvvis_files(monkeypatch):
    archive = get_archive('KIT_TeSt_20261105_0_0_1.uvvis.csv', monkeypatch)
    normalize_all(archive)

    assert archive.metadata.entry_type == 'peroTF_UVvisMeasurement'
    (uvvis,) = archive.data.figures
    assert uvvis.label == 'UV-vis'
    assert [trace['name'] for trace in uvvis.figure['data']] == [
        'reflection',
        'transmission',
        'absorption',
    ]
    delete_json()


def test_xrd_files(monkeypatch):
    archive = get_archive('KIT_TeSt_20261105_0_0_1.xrd.xy', monkeypatch)
    normalize_all(archive)

    assert archive.metadata.entry_type == 'peroTF_XRD_XY'
    (xrd,) = archive.data.figures
    assert xrd.label == 'XRD'
    assert len(xrd.figure['data'][0]['x']) == len(archive.data.data.angle)
    delete_json()


def test_experiment_file_all_processes(monkeypatch):
    """Every column Excel_creator writes ends up in the entries the parser creates."""
    file_name = os.path.join('tests', 'data', 'parsertest_all_processes.xlsx')
    excel = pd.read_excel(file_name, header=[0, 1])

    def cell(group, label):
        return excel[group][label].iloc[0]

    set_monkey_patch(monkeypatch)
    try:
        parse(file_name)
        entries = {
            file: parse(os.path.join('tests', 'data', file))[0].data
            for file in os.listdir(os.path.join('tests', 'data'))
            if file.endswith('.archive.json')
        }
    finally:
        delete_json()

    def entry(prefix):
        (data,) = [data for file, data in entries.items() if file.startswith(prefix)]
        return data

    sample = entries['KIT_PARSERTEST_20261103_0_0_1.archive.json']
    assert sample.datetime.date() == datetime.date(2026, 11, 3)
    multijunction = '21: Multijunction Info'
    assert sample.recombination_layer == cell(multijunction, 'Recombination Layer')
    assert sample.multijunction_notes == cell(multijunction, 'Notes')

    substrate = entry('0_substrate')
    assert substrate.number_of_pixels == cell('Experiment Info', 'Number of pixels')
    assert substrate.pixel_area.to('cm**2').magnitude == pytest.approx(
        cell('Experiment Info', 'Pixel area')
    )

    spin_coating = entry('3_0_spin_coating')
    assert spin_coating.spin_delay.to('s').magnitude == pytest.approx(
        cell('3: Spin Coating', 'Spin Delay [s]')
    )

    gas_quenching = entry('8_0_inkjet_printing').quenching
    assert gas_quenching.gas == cell('8: Inkjet Printing', 'Gas')
    assert gas_quenching.flow_rate.to('ml/s').magnitude == pytest.approx(
        cell('8: Inkjet Printing', 'Gas quenching flow rate [ml/s]')
    )
    vacuum_quenching = entry('9_0_inkjet_printing').quenching
    assert vacuum_quenching.duration.to('s').magnitude == pytest.approx(
        cell('9: Inkjet Printing', 'Vacuum quenching duration [s]')
    )

    assert len(entry('10_0_evaporation').organic_evaporation) == 1
    assert len(entry('11_0_evaporation').inorganic_evaporation) == 1

    for group, prefix, co_evaporation, materials in [
        ('12: Co-Evaporation', '12_0_coevaporation', True, 5),
        ('13: Seq-Evaporation', '13_0_evaporation', False, 3),
    ]:
        evaporation = entry(prefix)
        assert evaporation.co_evaporation is co_evaporation
        sources = evaporation.perovskite_evaporation
        assert [s.chemical_2.name for s in sources] == [
            cell(group, f'Material name {n}') for n in range(1, materials + 1)
        ]
        for n, source in enumerate(sources, start=1):
            assert source.thickness.to('nm').magnitude == pytest.approx(
                cell(group, f'Thickness {n} [nm]')
            )
            assert float(source.tooling_factor) == pytest.approx(
                cell(group, f'Tooling factor {n}')
            )

    lamination = entry('18_0_lamination')
    group = '18: Lamination'
    assert lamination.interface == cell(group, 'Interface')
    assert lamination.settings.temperature.to('degC').magnitude == pytest.approx(
        cell(group, 'Temperature during process[°C]')
    )
    assert lamination.settings.time.to('s').magnitude == pytest.approx(
        cell(group, 'Time lamination [s]')
    )
    assert lamination.settings.total_time.to('s').magnitude == pytest.approx(
        cell(group, 'Total time [s]')
    )
    assert lamination.settings.stamp_material == cell(group, 'Stamp 1 Material')
    assert lamination.settings.stamp_2_material == cell(group, 'Stamp 2 Material')
    assert lamination.settings.chamber_atmosphere == cell(
        group, 'Athmosphere in chamber'
    )
    assert lamination.atmosphere.relative_humidity == pytest.approx(
        cell(group, 'Humidity [%%rel]')
    )
    assert lamination.homogeneously_pressed is True
    assert lamination.successful_adhesion is True


def test_text_in_unit_columns_is_dropped():
    """A unit column with text must not abort the upload; the text is dropped."""
    df = pd.DataFrame(
        {
            ('Experiment Info', 'Nomad ID'): ['KIT_A_1', 'KIT_A_2'],
            ('1: Cleaning UV-Ozone', 'Temperature 1 [°C]'): ['RT', 25],
            ('1: Cleaning UV-Ozone', 'Solvent 1'): ['Water', 'IPA'],
            ('2: Lamination', 'Homogeniously pressed [1/0]'): ['yes', 0],
        }
    )
    warnings = []
    logger = type('Logger', (), {'warning': lambda self, m: warnings.append(m)})()

    cleaned = drop_text_in_unit_columns(df, logger)

    temperature = cleaned[('1: Cleaning UV-Ozone', 'Temperature 1 [°C]')]
    assert pd.isna(temperature[0])
    assert temperature[1] == 25
    assert list(cleaned[('1: Cleaning UV-Ozone', 'Solvent 1')]) == ['Water', 'IPA']
    assert list(cleaned[('2: Lamination', 'Homogeniously pressed [1/0]')]) == [
        'yes',
        0,
    ]
    assert len(warnings) == 1
    assert "'RT'" in warnings[0]
