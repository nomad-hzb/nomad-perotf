"""
Wrappers around baseclasses.helper.solar_cell_batch_mapping that read every column
Excel_creator writes. baseclasses is shared with other groups and stays unchanged;
whatever its map_* functions miss is added here.

Inventory IDs: every substance can have a '... chemical ID' column next to the
column with its name. baseclasses reads them for solutions ('Solvent N chemical ID',
'Solute N chemical ID', 'Additive N chemical ID'); add_chemical_id handles the rest.
"""

import re

import pandas as pd
from baseclasses import PubChemPureSubstanceSectionCustom
from baseclasses.atmosphere import Atmosphere
from baseclasses.helper.solar_cell_batch_mapping import (
    get_datetime,
    get_reference,
    get_value,
    map_gas_quenching_with_nozzle,
    map_vacuum_quenching,
)
from baseclasses.helper.solar_cell_batch_mapping import (
    map_atomic_layer_deposition as bc_map_atomic_layer_deposition,
)
from baseclasses.helper.solar_cell_batch_mapping import (
    map_cleaning as bc_map_cleaning,
)
from baseclasses.helper.solar_cell_batch_mapping import (
    map_close_space_sublimation as bc_map_close_space_sublimation,
)
from baseclasses.helper.solar_cell_batch_mapping import (
    map_evaporation as bc_map_evaporation,
)
from baseclasses.helper.solar_cell_batch_mapping import (
    map_inkjet_printing as bc_map_inkjet_printing,
)
from baseclasses.helper.solar_cell_batch_mapping import (
    map_spin_coating as bc_map_spin_coating,
)
from baseclasses.helper.solar_cell_batch_mapping import (
    map_sputtering as bc_map_sputtering,
)
from baseclasses.vapour_based_deposition.evaporation import (
    InorganicEvaporation,
    OrganicEvaporation,
    PerovskiteEvaporation,
)
from nomad.datamodel.metainfo.basesections import CompositeSystemReference

from nomad_perotf.schema_packages.perotf_package import (
    peroTF_LaminationSettings,
    peroTF_SubstanceWithID,
)


def add_chemical_id(section, sub_section, data, key):
    """
    Stores the inventory ID of column key with the substance in
    section.sub_section, which becomes a peroTF_SubstanceWithID for that. Nothing
    changes when the column is empty or there is no substance.
    """
    chemical_id = get_value(data, key, None, False)
    substance = getattr(section, sub_section, None)
    if chemical_id is None or substance is None:
        return
    substance = peroTF_SubstanceWithID.m_from_dict(substance.m_to_dict())
    substance.chemical_id = chemical_id
    setattr(section, sub_section, substance)


def get_flag(data, key):
    """A [1/0] column as bool, None if empty."""
    value = get_value(data, key, None, False)
    if value is None:
        return None
    return value.lower() in ('1', '1.0', 'true', 'yes', 'y', 'x', 'ja')


def numbered_materials(data):
    """Suffixes ' 1', ' 2', ... of all 'Material name N' columns, in order."""
    numbers = [
        int(match.group(1))
        for key in data.index
        if isinstance(key, str) and (match := re.fullmatch(r'Material name (\d+)', key))
    ]
    return [f' {n}' for n in sorted(numbers)]


def map_evaporation_source(data, mat, evaporation):
    """Copy of the per-source loop body of baseclasses map_evaporation."""
    if get_value(data, f'Source temperature start{mat}[°C]', None) and get_value(
        data, f'Source temperature end{mat}[°C]', None
    ):
        evaporation.temparature = [
            get_value(data, f'Source temperature start{mat}[°C]', None, unit='°C'),
            get_value(data, f'Source temperature end{mat}[°C]', None, unit='°C'),
        ]

    evaporation.thickness = get_value(data, f'Thickness{mat} [nm]', unit='nm')
    evaporation.start_rate = get_value(
        data, f'Rate start{mat} [angstrom/s]', unit='angstrom/s'
    )
    evaporation.target_rate = get_value(
        data,
        [f'Rate{mat} [angstrom/s]', f'Rate target{mat} [angstrom/s]'],
        unit=['angstrom/s', 'angstrom/s'],
    )
    evaporation.substrate_temparature = get_value(
        data, f'Substrate temperature{mat} [°C]', unit='°C'
    )
    evaporation.pressure = get_value(
        data,
        [f'Base pressure{mat} [bar]', f'Base pressure{mat} [mbar]'],
        None,
        unit=['bar', 'mbar'],
    )
    evaporation.pressure_start = get_value(
        data,
        [f'Pressure start{mat} [bar]', f'Pressure start{mat} [mbar]'],
        None,
        unit=['bar', 'mbar'],
    )
    evaporation.pressure_end = get_value(
        data,
        [f'Pressure end{mat} [bar]', f'Pressure end{mat} [mbar]'],
        None,
        unit=['bar', 'mbar'],
    )
    evaporation.tooling_factor = get_value(data, f'Tooling factor{mat}')
    evaporation.sample_holder = get_value(
        data, 'Sample holder width [mm]', None, unit='mm'
    )
    evaporation.chemical_2 = PubChemPureSubstanceSectionCustom(
        name=get_value(data, f'Material name{mat}', None, False), load_data=False
    )
    add_chemical_id(evaporation, 'chemical_2', data, f'Material chemical ID{mat}')
    return evaporation


def map_evaporation(i, j, lab_ids, data, upload_id, evaporation_class, col, logger):  # noqa: PLR0917
    """
    Evaporation, Co-Evaporation and Seq-Evaporation.

    Co- and Seq-Evaporation share their columns ('Material name N', ... for any N);
    their sources go to perovskite_evaporation. Seq-Evaporation keeps the file name
    of existing entries ('_evaporation_') and co_evaporation=False.
    """
    multi_source = 'Co-Evaporation' in col or 'Seq-Evaporation' in col
    file_name, archive = bc_map_evaporation(
        i,
        j,
        lab_ids,
        data,
        upload_id,
        evaporation_class,
        'Co-Evaporation' in col,
    )

    if multi_source:
        archive.perovskite_evaporation = [
            map_evaporation_source(data, mat, PerovskiteEvaporation())
            for mat in numbered_materials(data)
            if not pd.isna(data.get(f'Material name{mat}'))
        ]
        return file_name, archive

    organic = get_value(data, 'Organic', '', False).lower()
    if organic.startswith(('y', '1', 't')):
        source = OrganicEvaporation()
        if get_value(data, 'Temperature [°C]', None):
            source.temparature = [get_value(data, 'Temperature [°C]', None)] * 2
    else:
        if not organic.startswith(('n', '0', 'f')):
            logger.warning(
                f"{col}: 'Organic' is {data.get('Organic')!r}, expected true/false, "
                'yes/no or 1/0. The source is stored as inorganic_evaporation.'
            )
        source = InorganicEvaporation()
    map_evaporation_source(data, '', source)

    # replaces the sources baseclasses made: it drops the source when 'Organic' is empty
    archive.organic_evaporation = []
    archive.inorganic_evaporation = []
    if isinstance(source, InorganicEvaporation):
        archive.inorganic_evaporation = [source]
    else:
        archive.organic_evaporation = [source]
    return file_name, archive


def map_lamination(i, j, lab_ids, data, upload_id, lamination_class):  # noqa: PLR0917
    """
    Lamination with Excel_creator's column names. The names map_lamination of
    baseclasses reads stay as fallback for older files. Not a wrapper: baseclasses
    builds a LaminationSettings, which does not fit peroTF_Lamination.settings.
    """
    archive = lamination_class(
        name='Lamination',
        location=get_value(data, 'Tool/GB name', '', False),
        positon_in_experimental_plan=i,
        datetime=get_datetime(data, 'Datetime'),
        operator=get_value(data, 'Operator', '', False),
        description=get_value(data, 'Notes', '', False),
        samples=[
            CompositeSystemReference(
                reference=get_reference(upload_id, f'{lab_id}.archive.json'),
                lab_id=lab_id,
            )
            for lab_id in lab_ids
        ],
    )
    archive.settings = peroTF_LaminationSettings(
        temperature=get_value(
            data, ['Temperature during process[°C]', 'Temperature [°C]'], None
        ),
        temperature_at_pressure_relief=get_value(
            data, 'Temperature at pressure relief [°C]', None
        ),
        pressure=get_value(data, 'Pressure [MPa]', None),
        force=get_value(data, 'Force [N]', None),
        area=get_value(data, 'Area [mm²]', None),
        time=get_value(data, ['Time lamination [s]', 'Time [s]'], None),
        heat_up_time=get_value(data, 'Heat up time [s]', None),
        cool_down_time=get_value(data, 'Cool down time [s]', None),
        total_time=get_value(data, 'Total time [s]', None),
        chamber_atmosphere=get_value(data, 'Athmosphere in chamber', None, False),
        stamp_material=get_value(
            data, ['Stamp 1 Material', 'Stamp Material'], None, False
        ),
        stamp_thickness=get_value(
            data, ['Stamp 1 Thickness [mm]', 'Stamp Thickness [mm]'], None
        ),
        stamp_area=get_value(data, ['Stamp 1 Area [mm^2]', 'Stamp Area [mm²]'], None),
        stamp_2_material=get_value(data, 'Stamp 2 Material', None, False),
        stamp_2_thickness=get_value(data, 'Stamp 2 Thickness [mm]', None),
        stamp_2_area=get_value(data, 'Stamp 2 Area [mm^2]', None),
    )
    # Excel_creator writes the doubled '%%' literally
    humidity = get_value(data, ['Humidity [%%rel]', 'Humidity [%rel]'], None)
    if humidity is not None:
        archive.atmosphere = Atmosphere(relative_humidity=humidity)
    archive.interface = get_value(data, 'Interface', None, False)
    archive.homogeneously_pressed = get_flag(data, 'Homogeniously pressed [1/0]')
    archive.successful_adhesion = get_flag(data, 'Sucessful adhesion [1/0]')
    return f'{i}_{j}_lamination', archive


def map_spin_coating(i, j, lab_ids, data, upload_id, sc_class):  # noqa: PLR0917
    file_name, archive = bc_map_spin_coating(i, j, lab_ids, data, upload_id, sc_class)
    archive.spin_delay = get_value(data, 'Spin Delay [s]', None)
    add_chemical_id(
        archive.quenching, 'anti_solvent_2', data, 'Anti solvent chemical ID'
    )
    return file_name, archive


def map_cleaning(i, j, lab_ids, data, upload_id, cleaning_class):  # noqa: PLR0917
    file_name, archive = bc_map_cleaning(i, j, lab_ids, data, upload_id, cleaning_class)
    # baseclasses makes one entry per non-empty 'Solvent N', in this order
    numbers = [n for n in range(10) if get_value(data, f'Solvent {n}', None, False)]
    for n, cleaning in zip(numbers, archive.cleaning):
        add_chemical_id(cleaning, 'solvent_2', data, f'Solvent {n} chemical ID')
    return file_name, archive


def map_close_space_sublimation(i, j, lab_ids, data, upload_id, css_class):  # noqa: PLR0917
    file_name, archive = bc_map_close_space_sublimation(
        i, j, lab_ids, data, upload_id, css_class
    )
    process = archive.process
    # baseclasses makes one source material per non-empty name, in this order
    suffixes = [
        mat
        for mat in ['', ' 1', ' 2', ' 3', ' 4']
        if get_value(
            data, [f'Source material name{mat}', f'Source material{mat}'], None, False
        )
    ]
    for mat, source in zip(suffixes, process.source_material_mixture):
        add_chemical_id(
            source, 'source_material', data, f'Source material chemical ID{mat}'
        )
    if process.source_material_mixture:
        # baseclasses also keeps the first source material in chemical_2
        process.chemical_2 = process.source_material_mixture[0].source_material.m_copy(
            deep=True
        )
    return file_name, archive


def map_sputtering(i, j, lab_ids, data, upload_id, sputter_class):  # noqa: PLR0917
    file_name, archive = bc_map_sputtering(
        i, j, lab_ids, data, upload_id, sputter_class
    )
    add_chemical_id(archive.processes[0], 'target_2', data, 'Material chemical ID')
    return file_name, archive


def map_atomic_layer_deposition(i, j, lab_ids, data, upload_id, ald_class):  # noqa: PLR0917
    file_name, archive = bc_map_atomic_layer_deposition(
        i, j, lab_ids, data, upload_id, ald_class
    )
    properties = archive.properties
    add_chemical_id(properties.material, 'material', data, 'Precursor 1 chemical ID')
    add_chemical_id(
        properties.oxidizer_reducer, 'material', data, 'Precursor 2 chemical ID'
    )
    return file_name, archive


def map_inkjet_printing(i, j, lab_ids, data, upload_id, inkjet_class):  # noqa: PLR0917
    """baseclasses only reads GAVD columns for quenching; Excel_creator writes the
    gas and vacuum quenching columns of spin coating."""
    file_name, archive = bc_map_inkjet_printing(
        i, j, lab_ids, data, upload_id, inkjet_class
    )
    if archive.quenching is None:
        archive.quenching = map_vacuum_quenching(data) or map_gas_quenching_with_nozzle(
            data
        )
    return file_name, archive
