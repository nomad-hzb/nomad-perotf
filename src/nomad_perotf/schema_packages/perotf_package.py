# from nomad.units import ureg
import datetime

from baseclasses import BaseMeasurement, BaseProcess, Batch, LayerDeposition
from baseclasses.characterizations import XRD
from baseclasses.chemical import Chemical
from baseclasses.experimental_plan import ExperimentalPlan
from baseclasses.helper.utilities import (
    convert_datetime,
    get_encoding,
    set_sample_reference,
)
from baseclasses.material_processes_misc import (
    Annealing,
    Cleaning,
    PlasmaCleaning,
    SolutionCleaning,
    UVCleaning,
)
from baseclasses.solar_energy import (
    # PLMeasurement,
    UVvisMeasurement,
    EQEMeasurement,
    # TimeResolvedPhotoluminescence,
    JVMeasurement,
    MPPTracking,
    PLImaging,
    SolarCellProperties,
    # OpticalMicroscope,
    SolcarCellSample,
    StandardSampleSolarCell,
    Substrate,
)
from baseclasses.solution import Solution
from baseclasses.vapour_based_deposition import (
    ALDPropertiesIris,
    AtomicLayerDeposition,
    CloseSpaceSublimation,
    Evaporations,
    Sputtering,
)
from baseclasses.wet_chemical_deposition import (
    BladeCoating,
    DipCoating,
    InkjetPrinting,
    SlotDieCoating,
    SpinCoating,
    SpinCoatingRecipe,
    WetChemicalDeposition,
)
from nomad.datamodel.data import EntryData
from nomad.datamodel.results import ELN, Material, Properties, Results
from nomad.metainfo import Quantity, SchemaPackage, Section, SubSection

m_package = SchemaPackage(name='peroTF', aliases=['perotf_s'])

# %% ####################### Entities


class peroTF_ExperimentalPlan(ExperimentalPlan, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['users'],
            properties=dict(
                order=[
                    'name',
                    'standard_plan',
                    'load_standard_processes',
                    'create_samples_and_processes',
                    'number_of_substrates',
                    'substrates_per_subbatch',
                    'lab_id',
                ]
            ),
        ),
        a_template=dict(institute='KIT_perotf'),
    )

    solar_cell_properties = SubSection(section_def=SolarCellProperties)

    def normalize(self, archive, logger):
        super().normalize(archive, logger)

        from baseclasses.helper.execute_solar_sample_plan import (
            execute_solar_sample_plan,
        )

        execute_solar_sample_plan(self, archive, peroTF_Sample, peroTF_Batch, logger)

        # actual normalization!!
        archive.results = Results()
        archive.results.properties = Properties()
        archive.results.material = Material()
        archive.results.eln = ELN()
        archive.results.eln.sections = ['peroTF_ExperimentalPlan']


class peroTF_StandardSample(StandardSampleSolarCell, EntryData):
    m_def = Section(a_eln=dict(hide=['lab_id', 'users']))


class peroTF_SpinCoating_Recipe(SpinCoatingRecipe, EntryData):
    m_def = Section(a_eln=dict(hide=['lab_id', 'users']))


class peroTF_Chemical(Chemical, EntryData):
    m_def = Section(a_eln=dict(hide=['lab_id', 'users']))


# class peroTF_Powder(Powder, EntryData):
#     m_def = Section(
#         a_eln=dict(hide=['lab_id', 'users']))


# class peroTF_Solid(Solid, EntryData):
#     m_def = Section(
#         a_eln=dict(hide=['lab_id', 'users']))


# class peroTF_Gas(Gas, EntryData):
#     m_def = Section(
#         a_eln=dict(hide=['lab_id', 'users']))


class peroTF_Substrate(Substrate, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['users'],
            properties=dict(
                order=[
                    'name',
                    'substrate',
                    'conducting_material',
                    'solar_cell_area',
                    'pixel_area',
                    'number_of_pixels',
                ]
            ),
        )
    )


class peroTF_Solution(Solution, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'users',
                'components',
                'elemental_composition',
                'method',
                'temperature',
                'time',
                'speed',
                'solvent_ratio',
                'washing',
            ],
            properties=dict(
                order=[
                    'name',
                    'datetime',
                    'lab_id',
                    'description',
                    'preparation',
                    'solute',
                    'solvent',
                    'other_solution',
                    'additive',
                    'storage',
                ],
            ),
        ),
        a_template=dict(temperature=45, time=15, method='Shaker'),
    )


class peroTF_Sample(SolcarCellSample, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['users'], properties=dict(order=['name', 'substrate', 'architecture'])
        ),
        a_template=dict(institute='KIT_taskforce'),
        label_quantity='sample_id',
    )


class peroTF_Batch(Batch, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['users', 'samples'],
            properties=dict(
                order=['name', 'samples', 'export_batch_ids', 'csv_export_file']
            ),
        )
    )


# %% ####################### Cleaning


class peroTF_Cleaning(Cleaning, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'end_time', 'steps', 'instruments', 'present'],
            properties=dict(
                order=[
                    'name',
                    'present',
                    'datetime',
                    'previous_process',
                    'batch',
                    'samples',
                ]
            ),
        )
    )

    cleaning = SubSection(section_def=SolutionCleaning, repeats=True)

    cleaning_uv = SubSection(section_def=UVCleaning, repeats=True)

    cleaning_plasma = SubSection(section_def=PlasmaCleaning, repeats=True)


class peroTF_CR_Wetbench_Cleaning(Cleaning, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'location', 'end_time', 'steps', 'instruments'],
            properties=dict(
                order=[
                    'name',
                    'present',
                    'datetime',
                    'previous_process',
                    'batch',
                    'samples',
                ]
            ),
        )
    )

    cleaning = SubSection(section_def=SolutionCleaning, repeats=True)


# class peroTF_114_HyFlowBox_Cleaning_UV(Cleaning, EntryData):
#     m_def = Section(
#         a_eln=dict(
#             hide=[
#                 'lab_id', 'users', 'location', 'end_time',  'steps', 'instruments']))

#     cleaning = SubSection(
#         section_def=UVCleaning, repeats=True)


class peroTF_CR_Plasma_Cleaning(Cleaning, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'location', 'end_time', 'steps', 'instruments'],
            properties=dict(
                order=[
                    'name',
                    'present',
                    'datetime',
                    'previous_process',
                    'batch',
                    'samples',
                ]
            ),
        )
    )

    cleaning = SubSection(section_def=PlasmaCleaning, repeats=True)


# %% ##################### Layer Deposition


# class peroTF_114_HTFumeHood_SprayPyrolysis(SprayPyrolysis, EntryData):
#     m_def = Section(
#         a_eln=dict(
#             hide=[
#                 'lab_id', 'layer', 'user', 'author']))


class peroTF_BladeCoating(BladeCoating, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'end_time',
                'steps',
                'instruments',
                'results',
                'present',
            ],
            properties=dict(
                order=[
                    'name',
                    'location',
                    'present',
                    'datetime',
                    'batch',
                    'samples',
                    'solution',
                    'layer',
                    'quenching',
                    'annealing',
                ]
            ),
        )
    )


# %% ### Spin Coating
class peroTF_SpinCoating(SpinCoating, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'end_time', 'steps', 'instruments', 'present'],
            properties=dict(
                order=[
                    'name',
                    'present',
                    'recipe',
                    'datetime',
                    'previous_process',
                    'batch',
                    'samples',
                    'solution',
                    'layer',
                    'quenching',
                    'annealing',
                ]
            ),
        ),
    )


class peroTF_CR_SpinBox_SpinCoating(SpinCoating, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'location', 'end_time', 'steps', 'instruments'],
            properties=dict(
                order=[
                    'name',
                    'present',
                    'recipe',
                    'datetime',
                    'previous_process',
                    'batch',
                    'samples',
                    'solution',
                    'layer',
                    'quenching',
                    'annealing',
                ]
            ),
        ),
        a_template=dict(
            layer_type='Absorber Layer',
        ),
    )


class peroTF_CR_ChemistryBox_SpinCoating(SpinCoating, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'location', 'end_time', 'steps', 'instruments'],
            properties=dict(
                order=[
                    'name',
                    'present',
                    'recipe',
                    'datetime',
                    'previous_process',
                    'batch',
                    'samples',
                    'solution',
                    'layer',
                    'quenching',
                    'annealing',
                ]
            ),
        ),
        a_template=dict(
            layer_type='Absorber Layer',
        ),
    )


class peroTF_CR_MixBox_SpinCoating(SpinCoating, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'location', 'end_time', 'steps', 'instruments'],
            properties=dict(
                order=[
                    'name',
                    'present',
                    'recipe',
                    'datetime',
                    'previous_process',
                    'batch',
                    'samples',
                    'solution',
                    'layer',
                    'quenching',
                    'annealing',
                ]
            ),
        ),
        a_template=dict(
            layer_type='Hole Transport Layer',
        ),
    )


class peroTF_CR_OmegaBox_SpinCoating(SpinCoating, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'location', 'end_time', 'steps', 'instruments'],
            properties=dict(
                order=[
                    'name',
                    'present',
                    'recipe',
                    'datetime',
                    'previous_process',
                    'batch',
                    'samples',
                    'solution',
                    'layer',
                    'quenching',
                    'annealing',
                ]
            ),
        ),
        a_template=dict(
            layer_type='Absorber Layer',
        ),
    )


class peroTF_TFL_AlphaBox_SpinCoating(SpinCoating, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'location', 'end_time', 'steps', 'instruments'],
            properties=dict(
                order=[
                    'name',
                    'present',
                    'recipe',
                    'datetime',
                    'previous_process',
                    'batch',
                    'samples',
                    'solution',
                    'layer',
                    'quenching',
                    'annealing',
                ]
            ),
        ),
        a_template=dict(
            layer_type='Absorber Layer',
        ),
    )


class peroTF_CR_BetaBox_SpinCoating(SpinCoating, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'location', 'end_time', 'steps', 'instruments'],
            properties=dict(
                order=[
                    'name',
                    'present',
                    'recipe',
                    'datetime',
                    'previous_process',
                    'batch',
                    'samples',
                    'solution',
                    'layer',
                    'quenching',
                    'annealing',
                ]
            ),
        ),
        a_template=dict(
            layer_type='Absorber Layer',
        ),
    )


# %% ### Slot Die Coating
class peroTF_SlotDieCoating(SlotDieCoating, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'end_time', 'steps', 'instruments', 'present'],
            properties=dict(
                order=[
                    'name',
                    'present',
                    'datetime',
                    'previous_process',
                    'batch',
                    'samples',
                    'solution',
                    'layer',
                    'properties',
                    'quenching',
                    'annealing',
                ]
            ),
        ),
    )


class peroTF_UP_SlotDieBox_SlotDieCoating(SlotDieCoating, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'location', 'end_time', 'steps', 'instruments'],
            properties=dict(
                order=[
                    'name',
                    'present',
                    'datetime',
                    'previous_process',
                    'batch',
                    'samples',
                    'solution',
                    'layer',
                    'properties',
                    'quenching',
                    'annealing',
                ]
            ),
        ),
        a_template=dict(layer_type='Absorber Layer'),
    )


# # %% ### Annealing
class peroTF_ThermalAnnealing(BaseProcess, EntryData):
    annealing = SubSection(
        links=['http://purl.obolibrary.org/obo/RO_0001019'], section_def=Annealing
    )

    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'end_time',
                'steps',
                'instruments',
                'humidity',
                'present',
            ],
            properties=dict(
                order=[
                    'name',
                    'datetime',
                    'batch',
                    'samples',
                ]
            ),
        ),
        a_template=dict(
            layer_type='Absorber Layer',
        ),
    )


class peroTF_CR_ThermalAnnealing(BaseProcess, EntryData):
    annealing = SubSection(
        links=['http://purl.obolibrary.org/obo/RO_0001019'], section_def=Annealing
    )

    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time',
                'steps',
                'instruments',
                'humidity',
            ],
            properties=dict(
                order=[
                    'name',
                    'present',
                    'datetime',
                    'temperature',
                    'time',
                    'atmosphere',
                    'function',
                    'previous_process',
                    'batch',
                    'samples',
                ]
            ),
        ),
        a_template=dict(
            layer_type='Absorber Layer',
        ),
    )


class peroTF_TFL_ThermalAnnealing(BaseProcess, EntryData):
    annealing = SubSection(
        links=['http://purl.obolibrary.org/obo/RO_0001019'], section_def=Annealing
    )

    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time',
                'steps',
                'instruments',
                'humidity',
            ],
            properties=dict(
                order=[
                    'name',
                    'present',
                    'datetime',
                    'temperature',
                    'time',
                    'atmosphere',
                    'function',
                    'previous_process',
                    'batch',
                    'samples',
                ]
            ),
        ),
        a_template=dict(
            layer_type='Absorber Layer',
        ),
    )


# %% ### Atomic Layer Deposition
class peroTF_ALD(AtomicLayerDeposition, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'end_time',
                'steps',
                'instruments',
                'results',
                'present',
            ],
            properties=dict(
                order=[
                    'name',
                    'present',
                    'datetime',
                    'batch',
                    'samples',
                    'layer',
                ]
            ),
        )
    )

    properties = SubSection(section_def=ALDPropertiesIris)


# %% ### Evaporation
class peroTF_CloseSpaceSublimation(CloseSpaceSublimation, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'end_time', 'steps', 'instruments', 'present'],
            properties=dict(
                order=[
                    'name',
                    'location',
                    'present',
                    'datetime',
                    'batch',
                    'samples',
                    'layer',
                ]
            ),
        )
    )


class peroTF_Evaporation(Evaporations, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'end_time', 'steps', 'instruments', 'present'],
            properties=dict(
                order=[
                    'name',
                    'location',
                    'present',
                    'datetime',
                    'batch',
                    'samples',
                    'layer',
                ]
            ),
        )
    )


class peroTF_Sputtering(Sputtering, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'end_time', 'steps', 'instruments', 'present'],
            properties=dict(
                order=[
                    'name',
                    'present',
                    'datetime',
                    'batch',
                    'samples',
                    'layer',
                ]
            ),
        )
    )


class peroTF_TFL_SputterSystem_Sputtering(Sputtering, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'location', 'end_time', 'steps', 'instruments'],
            properties=dict(
                order=[
                    'name',
                    'present',
                    'datetime',
                    'previous_process',
                    'batch',
                    'samples',
                    'layer',
                ]
            ),
        )
    )


class peroTF_TFL_Ebeam_Evaporation(Evaporations, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'location', 'end_time', 'steps', 'instruments'],
            properties=dict(
                order=[
                    'name',
                    'present',
                    'datetime',
                    'previous_process',
                    'batch',
                    'samples',
                    'layer',
                ]
            ),
        )
    )


class peroTF_CR_Angstrom_Evaporation(Evaporations, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'location', 'end_time', 'steps', 'instruments'],
            properties=dict(
                order=[
                    'name',
                    'present',
                    'datetime',
                    'previous_process',
                    'batch',
                    'samples',
                    'layer',
                ]
            ),
        )
    )


class peroTF_TFL_BellJar_Evaporation(Evaporations, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'location', 'end_time', 'steps', 'instruments'],
            properties=dict(
                order=[
                    'name',
                    'present',
                    'datetime',
                    'previous_process',
                    'batch',
                    'samples',
                    'layer',
                ]
            ),
        )
    )


class peroTF_UP_PEROvap_Evaporation(Evaporations, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'location', 'end_time', 'steps', 'instruments'],
            properties=dict(
                order=[
                    'name',
                    'present',
                    'datetime',
                    'previous_process',
                    'batch',
                    'samples',
                    'layer',
                ]
            ),
        )
    )


class peroTF_TFL_PEROvap_Evaporation(Evaporations, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'location', 'end_time', 'steps', 'instruments'],
            properties=dict(
                order=[
                    'name',
                    'present',
                    'datetime',
                    'previous_process',
                    'batch',
                    'samples',
                    'layer',
                ]
            ),
        )
    )


class peroTF_UP_OPTIvap_Evaporation(Evaporations, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'location', 'end_time', 'steps', 'instruments'],
            properties=dict(
                order=[
                    'name',
                    'present',
                    'datetime',
                    'previous_process',
                    'batch',
                    'samples',
                    'layer',
                ]
            ),
        )
    )


# %% ## DipCoating


class peroTF_DipCoating(DipCoating, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'end_time', 'steps', 'instruments', 'present'],
            properties=dict(
                order=[
                    'name',
                    'present',
                    'datetime',
                    'previous_process',
                    'batch',
                    'samples',
                    'solution',
                    'layer',
                    'properties',
                    'quenching',
                    'annealing',
                ]
            ),
        ),
    )


# %% ## Printing


class peroTF_InkjetPrinting(InkjetPrinting, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'end_time', 'steps', 'instruments', 'present'],
            properties=dict(
                order=[
                    'name',
                    'present',
                    'datetime',
                    'previous_process',
                    'batch',
                    'samples',
                    'solution',
                    'layer',
                    'properties',
                    'quenching',
                    'annealing',
                ]
            ),
        ),
    )


# %% ## Storage


# class peroTF_108_HyDryAir_Storage(Storage, EntryData):
#     m_def = Section(
#         a_eln=dict(
#             hide=[
#                 'lab_id', 'users', 'location', 'end_time',  'steps', 'instruments']))


# %%####################################### Measurements


class peroTF_CR_SolSimBox_JVmeasurement(JVMeasurement, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time',
                'steps',
                'instruments',
                'results',
                'certified_values',
                'certification_institute',
            ],
            properties=dict(
                order=[
                    'name',
                    'data_file',
                    'active_area',
                    'intensity',
                    'integration_time',
                    'settling_time',
                    'averaging',
                    'compliance',
                    'samples',
                ]
            ),
        ),
        a_plot=[
            {
                'x': 'jv_curve/:/voltage',
                'y': 'jv_curve/:/current_density',
                'layout': {
                    'showlegend': True,
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
            }
        ],
    )

    multijunction_position = Quantity(
        type=str,
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=['top', 'mid', 'bottom']),
        ),
    )

    def normalize(self, archive, logger):
        super(JVMeasurement, self).normalize(archive, logger)
        self.method = 'JV Measurement'

        if self.data_file:
            from baseclasses.helper.utilities import get_encoding

            with archive.m_context.raw_file(self.data_file, 'br') as f:
                encoding = get_encoding(f)

            with archive.m_context.raw_file(
                self.data_file, 'rt', encoding=encoding
            ) as f:
                from baseclasses.helper.archive_builder.jv_archive import get_jv_archive

                from nomad_perotf.schema_packages.parsers.KIT_jv_parser import (
                    get_jv_data,
                )

                jv_dict = get_jv_data(f.read())
                try:
                    self.datetime = convert_datetime(
                        jv_dict['datetime'],
                        datetime_format='%Y-%m-%d %H:%M:%S %p',
                        utc=False,
                    )

                except Exception:
                    try:
                        self.datetime = convert_datetime(
                            jv_dict['datetime'],
                            datetime_format='%Y-%m-%d %H:%M:%S',
                            utc=False,
                        )
                    except Exception:
                        logger.warning('Couldnt parse datetime')

                get_jv_archive(jv_dict, self.data_file, self)

        super().normalize(archive, logger)


class peroTF_MPPTracking(MPPTracking, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time',
                'steps',
                'instruments',
                'results',
            ],
            properties=dict(order=['name', 'data_file', 'samples']),
        ),
        a_plot=[
            {
                'x': 'time',
                'y': ['power_density', 'voltage'],
                'layout': {
                    'showlegend': True,
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
            }
        ],
    )

    measurement_programm = Quantity(
        type=str,
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=['python', 'labview']),
        ),
    )

    def normalize(self, archive, logger):
        if not self.samples and self.data_file:
            search_id = self.data_file.split('.')[0]
            set_sample_reference(archive, self, search_id)

        if self.data_file:
            from baseclasses.helper.utilities import get_encoding

            with archive.m_context.raw_file(self.data_file, 'br') as f:
                encoding = get_encoding(f)

            with archive.m_context.raw_file(
                self.data_file, 'rt', encoding=encoding
            ) as f:
                from nomad_perotf.schema_packages.parsers.KIT_mpp_parser import (
                    get_mpp_archive,
                    get_mpp_data,
                )

                mpp_dict, data, file_type = get_mpp_data(f.read())
                self.measurement_programm = file_type
                get_mpp_archive(mpp_dict, file_type, data, self)
        super().normalize(archive, logger)


class peroTF_CR_SolSimBox_MPPTracking(MPPTracking, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time',
                'steps',
                'instruments',
                'results',
            ],
            properties=dict(order=['name', 'data_file', 'samples']),
        ),
        a_plot=[
            {
                'x': 'time',
                'y': ['power_density', 'voltage'],
                'layout': {
                    'showlegend': True,
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
            }
        ],
    )

    def normalize(self, archive, logger):
        if self.data_file:
            from baseclasses.helper.utilities import get_encoding

            with archive.m_context.raw_file(self.data_file, 'br') as f:
                encoding = get_encoding(f)

            with archive.m_context.raw_file(
                self.data_file, 'rt', encoding=encoding
            ) as f:
                from nomad_perotf.schema_packages.parsers.KIT_mpp_parser import (
                    get_mpp_archive,
                    get_mpp_data,
                )

                mpp_dict, data, file_type = get_mpp_data(f.read())
                get_mpp_archive(mpp_dict, file_type, data, self)
        super().normalize(archive, logger)


class peroTF_TFL_GammaBox_JVmeasurement(JVMeasurement, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time',
                'steps',
                'instruments',
                'results',
                'certified_values',
                'certification_institute',
            ],
            properties=dict(
                order=[
                    'name',
                    'data_file',
                    'active_area',
                    'intensity',
                    'integration_time',
                    'settling_time',
                    'averaging',
                    'compliance',
                    'samples',
                ]
            ),
        ),
        a_plot=[
            {
                'x': 'jv_curve/:/voltage',
                'y': 'jv_curve/:/current_density',
                'layout': {
                    'showlegend': True,
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
            }
        ],
    )

    multijunction_position = Quantity(
        type=str,
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=['top', 'mid', 'bottom']),
        ),
    )

    def normalize(self, archive, logger):
        super(JVMeasurement, self).normalize(archive, logger)
        self.method = 'JV Measurement'

        if self.data_file:
            from baseclasses.helper.utilities import get_encoding

            with archive.m_context.raw_file(self.data_file, 'br') as f:
                encoding = get_encoding(f)

            with archive.m_context.raw_file(
                self.data_file, 'tr', encoding=encoding
            ) as f:
                from baseclasses.helper.archive_builder.jv_archive import get_jv_archive

                from nomad_perotf.schema_packages.parsers.KIT_jv_parser import (
                    get_jv_data,
                )

                jv_dict = get_jv_data(f.read())
                try:
                    self.datetime = convert_datetime(
                        jv_dict['datetime'],
                        datetime_format='%Y-%m-%d %H:%M:%S %p',
                        utc=False,
                    )

                except Exception:
                    try:
                        self.datetime = convert_datetime(
                            jv_dict['datetime'],
                            datetime_format='%Y-%m-%d %H:%M:%S',
                            utc=False,
                        )
                    except Exception:
                        logger.warning('Couldnt parse datetime')
                get_jv_archive(jv_dict, self.data_file, self)

        super().normalize(archive, logger)

class peroTF_UVvisMeasurement(UVvisMeasurement, EntryData):
    pass
class peroTF_JVmeasurement(JVMeasurement, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time',
                'steps',
                'instruments',
                'results',
                'certified_values',
                'certification_institute',
            ],
            properties=dict(
                order=[
                    'name',
                    'data_file',
                    'active_area',
                    'intensity',
                    'integration_time',
                    'settling_time',
                    'averaging',
                    'compliance',
                    'samples',
                ]
            ),
        ),
        a_plot=[
            {
                'x': 'jv_curve/:/voltage',
                'y': 'jv_curve/:/current_density',
                'layout': {
                    'showlegend': True,
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
            }
        ],
    )

    multijunction_position = Quantity(
        type=str,
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=['top', 'mid', 'bottom']),
        ),
    )

    data_file_reverse = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'),
    )

    measurement_programm = Quantity(
        type=str,
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=['python', 'labview']),
        ),
    )

    def map_jv_measurement(self, file, archive, logger):
        with archive.m_context.raw_file(file, 'br') as f:
            encoding = get_encoding(f)

        with archive.m_context.raw_file(file, 'tr', encoding=encoding) as f:
            from nomad_perotf.schema_packages.parsers.KIT_jv_parser import (
                get_jv_data,
            )

            jv_dict = get_jv_data(f.read())
            try:
                self.datetime = convert_datetime(
                    file.split('.')[-3][-15:],
                    datetime_format='%Y%m%dT%H%M%S',
                    utc=False,
                )
            except Exception:
                try:
                    self.datetime = convert_datetime(
                        jv_dict['datetime'],
                        datetime_format='%Y-%m-%d %H:%M:%S %p',
                        utc=False,
                    )

                except Exception:
                    try:
                        self.datetime = convert_datetime(
                            jv_dict['datetime'],
                            datetime_format='%Y-%m-%d %H:%M:%S',
                            utc=False,
                        )
                    except Exception:
                        logger.warning('Couldnt parse datetime')
            return jv_dict

    def normalize(self, archive, logger):
        super(JVMeasurement, self).normalize(archive, logger)
        self.method = 'JV Measurement'
        from baseclasses.helper.archive_builder.jv_archive import get_jv_archive

        if not self.samples and self.data_file:
            search_id = self.data_file.split('.')[0]
            set_sample_reference(archive, self, search_id)

        if self.data_file:
            from nomad_perotf.schema_packages.parsers.KIT_jv_parser import (
                identify_file_type,
            )

            with archive.m_context.raw_file(self.data_file, 'br') as f:
                encoding = get_encoding(f)
            with archive.m_context.raw_file(
                self.data_file, 'tr', encoding=encoding
            ) as f:
                self.measurement_programm = identify_file_type(f.read())

        if (
            not self.data_file_reverse
            and self.data_file
            and self.measurement_programm == 'python'
        ):
            test_string = self.data_file.replace('fwd', 'rev')[:-21]
            fwd_time = datetime.datetime.strptime(
                self.data_file.split('.')[-3][-15:], '%Y%m%dT%H%M%S'
            )
            for file in archive.m_context.upload_files.raw_directory_list():
                if not file.path.startswith(test_string) and file.path.endswith(
                    'jv.txt'
                ):
                    continue
                try:
                    rew_time = datetime.datetime.strptime(
                        file.path.split('.')[-3][-15:], '%Y%m%dT%H%M%S'
                    )
                except Exception:
                    continue

                if (
                    datetime.timedelta(seconds=1)
                    < rew_time - fwd_time
                    < datetime.timedelta(minutes=1)
                ):
                    self.data_file_reverse = file.path

        if self.data_file:
            jv_dict = self.map_jv_measurement(self.data_file, archive, logger)
            if self.data_file_reverse:
                jv_dict['jv_curve'][0]['name'] = 'Forward Scan'
            get_jv_archive(jv_dict, self.data_file, self)

        if self.data_file and self.data_file_reverse:
            jv_dict_ref = self.map_jv_measurement(
                self.data_file_reverse, archive, logger
            )
            jv_dict_ref['jv_curve'][0]['name'] = 'Reverse Scan'
            get_jv_archive(jv_dict_ref, self.data_file_reverse, self, append=True)

        super().normalize(archive, logger)


class peroTF_TFL_GammaBox_EQEmeasurement(EQEMeasurement, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time',
                'steps',
                'instruments',
                'results',
            ],
            properties=dict(order=['name', 'data_file', 'samples']),
        )
    )

    multijunction_position = Quantity(
        type=str,
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=['top', 'mid', 'bottom']),
        ),
    )


class peroTF_PLImaging(PLImaging, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time',
                'steps',
                'instruments',
                'results',
                'solution',
            ],
            properties=dict(order=['name', 'data_file', 'samples']),
        )
    )


class KIT_XRD_XY_Simulated(XRD, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time',
                'steps',
                'instruments',
                'results',
                'steps',
                'instruments',
                'results',
                'metadata_file',
                'shifted_data',
                'identifier',
            ],
            properties=dict(order=['name', 'data_file', 'samples', 'solution']),
        ),
        a_plot=[
            {
                'x': ['data/angle'],
                'y': ['data/intensity'],
                'layout': {
                    'yaxis': {'fixedrange': False, 'title': 'Counts'},
                    'xaxis': {'fixedrange': False},
                },
            },
        ],
    )

    cif_string = Quantity(type=str)


# %%####################################### Generic Entries


class peroTF_Process(BaseProcess, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'location', 'end_time'],
            properties=dict(order=['name', 'data_file', 'batch', 'samples']),
        )
    )

    data_file = Quantity(
        type=str,
        shape=['*'],
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'),
    )


class peroTF_Deposition(LayerDeposition, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'location', 'end_time', 'instruments'],
            properties=dict(
                order=[
                    'name',
                    'layer_type',
                    'layer_material_name',
                    'layer_material',
                    'data_file',
                    'previous_process',
                    'batch',
                    'samples',
                ]
            ),
        )
    )

    data_file = Quantity(
        type=str,
        shape=['*'],
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'),
    )


class peroTF_WetChemicalDepoistion(WetChemicalDeposition, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'location', 'end_time', 'instruments'],
            properties=dict(
                order=[
                    'name',
                    'present',
                    'datetime',
                    'previous_process',
                    'batch',
                    'samples',
                    'solution',
                    'layer',
                    'quenching',
                    'annealing',
                ]
            ),
        )
    )

    data_file = Quantity(
        type=str,
        shape=['*'],
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'),
    )


class peroTF_Measurement(BaseMeasurement, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'location', 'end_time', 'instruments'],
            properties=dict(order=['name', 'data_file', 'samples']),
        )
    )

    data_file = Quantity(
        type=str,
        shape=['*'],
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'),
    )


m_package.__init_metainfo__()
