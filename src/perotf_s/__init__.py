# from nomad.units import ureg
from nomad.metainfo import (
    Package,
    Quantity,
    SubSection,
    Section)

from nomad.datamodel.data import EntryData
from nomad.datamodel.results import Results, Properties, Material, ELN

from baseclasses import (
    BaseProcess, BaseMeasurement, LayerDeposition, Batch
)

from baseclasses.chemical import (
    Chemical
)


from baseclasses.solution import Solution
from baseclasses.experimental_plan import ExperimentalPlan

from baseclasses.wet_chemical_deposition import (
    SpinCoating,
    SpinCoatingRecipe,
    SlotDieCoating,
    WetChemicalDeposition)

from baseclasses.vapour_based_deposition import (
    Evaporations, Sputtering)

from baseclasses.material_processes_misc import (
    Cleaning,
    SolutionCleaning,
    PlasmaCleaning,
)

from baseclasses.solar_energy import (
    StandardSampleSolarCell, SolarCellProperties,
    Substrate,
    # TimeResolvedPhotoluminescence,
    JVMeasurement,
    # PLMeasurement,
    # UVvisMeasurement,
    EQEMeasurement,
    # OpticalMicroscope,
    SolcarCellSample,
    MPPTracking
)

from baseclasses.helper.utilities import convert_datetime


m_package4 = Package(name='peroTF')

# %% ####################### Entities


class peroTF_ExperimentalPlan(ExperimentalPlan, EntryData):
    m_def = Section(
        a_eln=dict(hide=['users'],
                   properties=dict(
            order=[
                "name",
                "standard_plan",
                "load_standard_processes",
                "create_samples_and_processes",
                "number_of_substrates",
                "substrates_per_subbatch",
                "lab_id"
            ])),
        a_template=dict(institute="KIT_perotf"))

    solar_cell_properties = SubSection(
        section_def=SolarCellProperties)

    def normalize(self, archive, logger):
        super(peroTF_ExperimentalPlan, self).normalize(archive, logger)

        from baseclasses.helper.execute_solar_sample_plan import execute_solar_sample_plan
        execute_solar_sample_plan(self, archive, peroTF_Sample, peroTF_Batch, logger)

        # actual normalization!!
        archive.results = Results()
        archive.results.properties = Properties()
        archive.results.material = Material()
        archive.results.eln = ELN()
        archive.results.eln.sections = ["peroTF_ExperimentalPlan"]


class peroTF_StandardSample(StandardSampleSolarCell, EntryData):
    m_def = Section(
        a_eln=dict(hide=['lab_id', 'users']))


class peroTF_SpinCoating_Recipe(SpinCoatingRecipe, EntryData):
    m_def = Section(
        a_eln=dict(hide=['lab_id', 'users']))


class peroTF_Chemical(Chemical, EntryData):
    m_def = Section(
        a_eln=dict(hide=['lab_id', 'users']))


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
        a_eln=dict(hide=['lab_id', 'users'],
                   properties=dict(
            order=[
                "name",
                "substrate",
                "conducting_material",
                "solar_cell_area",
                "pixel_area",
                "number_of_pixels"])))


class peroTF_Solution(Solution, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'users', 'components', 'elemental_composition',  "method", "temperature", "time", "speed", "solvent_ratio", "washing"],
            properties=dict(
                order=[
                    "name",
                    "datetime",
                    "lab_id",
                    "description", "preparation", "solute", "solvent", "other_solution", "additive", "storage"
                ],
            )),
        a_template=dict(temperature=45, time=15, method='Shaker'))


class peroTF_Sample(SolcarCellSample, EntryData):
    m_def = Section(
        a_eln=dict(hide=['users'], properties=dict(
            order=["name", "substrate", "architecture"])),
        a_template=dict(institute="KIT_taskforce"),
        label_quantity='sample_id'
    )


class peroTF_Batch(Batch, EntryData):
    m_def = Section(
        a_eln=dict(hide=['users', 'samples'],
                   properties=dict(
            order=[
                "name",
                "samples",
                "export_batch_ids",
                "csv_export_file"])))


# %% ####################### Cleaning


class peroTF_CR_Wetbench_Cleaning(Cleaning, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'users', 'location', 'end_time',  'steps', 'instruments'],
            properties=dict(
                order=[
                    "name", "present",
                    "datetime", "previous_process",
                    "batch",
                    "samples"])))

    cleaning = SubSection(
        section_def=SolutionCleaning, repeats=True)


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
            hide=[
                'lab_id', 'users', 'location', 'end_time', 'steps', 'instruments'],
            properties=dict(
                order=[
                    "name", "present",
                    "datetime", "previous_process",
                    "batch",
                    "samples"])))

    cleaning = SubSection(
        section_def=PlasmaCleaning, repeats=True)


# %% ##################### Layer Deposition


# class peroTF_114_HTFumeHood_SprayPyrolysis(SprayPyrolysis, EntryData):
#     m_def = Section(
#         a_eln=dict(
#             hide=[
#                 'lab_id', 'layer', 'user', 'author']))


# %% ### Spin Coating

class peroTF_CR_SpinBox_SpinCoating(SpinCoating, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'users', 'location', 'end_time', 'steps', 'instruments'],
            properties=dict(
                order=[
                    "name",
                    "present",
                    "recipe"
                    "datetime", "previous_process",
                    "batch",
                    "samples",
                    "solution",
                    "layer",
                    "quenching",
                    "annealing"])), a_template=dict(
            layer_type="Absorber Layer",
        ))


class peroTF_CR_ChemistryBox_SpinCoating(SpinCoating, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'users', 'location', 'end_time',  'steps', 'instruments'],
            properties=dict(
                order=[
                    "name",
                    "present",
                    "recipe"
                    "datetime", "previous_process",
                    "batch",
                    "samples",
                    "solution",
                    "layer",
                    "quenching",
                    "annealing"])), a_template=dict(
            layer_type="Absorber Layer",
        ))


class peroTF_CR_MixBox_SpinCoating(SpinCoating, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'users', 'location', 'end_time',  'steps', 'instruments'],
            properties=dict(
                order=[
                    "name", "present",
                    "recipe"
                    "datetime", "previous_process",
                    "batch",
                    "samples",
                    "solution",
                    "layer",
                    "quenching",
                    "annealing"])), a_template=dict(
            layer_type="Hole Transport Layer",
        ))


class peroTF_CR_OmegaBox_SpinCoating(SpinCoating, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'users', 'location', 'end_time',  'steps', 'instruments'],
            properties=dict(
                order=[
                    "name", "present",
                    "recipe"
                    "datetime", "previous_process",
                    "batch",
                    "samples",
                    "solution",
                    "layer",
                    "quenching",
                    "annealing"])), a_template=dict(
            layer_type="Absorber Layer",
        ))


class peroTF_TFL_AlphaBox_SpinCoating(SpinCoating, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'users', 'location', 'end_time',  'steps', 'instruments'],
            properties=dict(
                order=[
                    "name", "present",
                    "recipe"
                    "datetime", "previous_process",
                    "batch",
                    "samples",
                    "solution",
                    "layer",
                    "quenching",
                    "annealing"])), a_template=dict(
            layer_type="Absorber Layer",
        ))


class peroTF_CR_BetaBox_SpinCoating(SpinCoating, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'users', 'location', 'end_time',  'steps', 'instruments'],
            properties=dict(
                order=[
                    "name", "present",
                    "recipe"
                    "datetime", "previous_process",
                    "batch",
                    "samples",
                    "solution",
                    "layer",
                    "quenching",
                    "annealing"])), a_template=dict(
            layer_type="Absorber Layer",
        ))


# %% ### Slot Die Coating


class peroTF_UP_SlotDieBox_SlotDieCoating(SlotDieCoating, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location', 'end_time',  'steps', 'instruments'],
            properties=dict(
                order=[
                    "name", "present",
                    "datetime", "previous_process",
                    "batch",
                    "samples",
                    "solution",
                    "layer",
                    "properties",
                    "quenching",
                    "annealing"])),
        a_template=dict(
            layer_type="Absorber Layer"))


# # %% ### Annealing

# class peroTF_CR_SpinBox_ThermalAnnealing(ThermalAnnealing, EntryData):
#     m_def = Section(
#         a_eln=dict(
#             hide=[
#                 'lab_id', 'users', 'location', 'end_time',  'steps', 'instruments', 'humidity'],
#             properties=dict(
#                 order=[
#                     "name",

#                     "temperature",
#                     "time",
#                     "function",
#                     "previous_process",
#                     "batch",
#                     "samples"])))


# class peroTF_CR_MixBox_ThermalAnnealing(ThermalAnnealing, EntryData):
#     m_def = Section(
#         a_eln=dict(
#             hide=[
#                 'lab_id', 'users', 'location', 'end_time',  'steps', 'instruments', 'humidity'],
#             properties=dict(
#                 order=[
#                     "name",

#                     "temperature",
#                     "time",
#                     "function",
#                     "previous_process",
#                     "batch",
#                     "samples"])))


# class peroTF_CR_ChemistryBox_ThermalAnnealing(ThermalAnnealing, EntryData):
#     m_def = Section(
#         a_eln=dict(
#             hide=[
#                 'lab_id', 'users', 'location', 'end_time',  'steps', 'instruments', 'humidity'],
#             properties=dict(
#                 order=[
#                     "name",

#                     "temperature",
#                     "time",
#                     "function",
#                     "previous_process",
#                     "batch",
#                     "samples"])))


# class peroTF_CR_OmegaBox_ThermalAnnealing(ThermalAnnealing, EntryData):
#     m_def = Section(
#         a_eln=dict(
#             hide=[
#                 'lab_id', 'users', 'location', 'end_time',  'steps', 'instruments', 'humidity'],
#             properties=dict(
#                 order=[
#                     "name",

#                     "temperature",
#                     "time",
#                     "function",
#                     "previous_process",
#                     "batch",
#                     "samples"])))


# class peroTF_CR_Wetbench_ThermalAnnealing(ThermalAnnealing, EntryData):
#     m_def = Section(
#         a_eln=dict(
#             hide=[
#                 'lab_id', 'users', 'location', 'end_time',  'steps', 'instruments', 'humidity'],
#             properties=dict(
#                 order=[
#                     "name",

#                     "temperature",
#                     "time",
#                     "function",
#                     "previous_process",
#                     "batch",
#                     "samples"])))


# class peroTF_CR_Fumehood_ThermalAnnealing(ThermalAnnealing, EntryData):
#     m_def = Section(
#         a_eln=dict(
#             hide=[
#                 'lab_id', 'users', 'location', 'end_time',  'steps', 'instruments', 'humidity'],
#             properties=dict(
#                 order=[
#                     "name",

#                     "temperature",
#                     "time",
#                     "function",
#                     "previous_process",
#                     "batch",
#                     "samples"])))


# class peroTF_TFL_AlphaBox_ThermalAnnealing(ThermalAnnealing, EntryData):
#     m_def = Section(
#         a_eln=dict(
#             hide=[
#                 'lab_id', 'users', 'location', 'end_time',  'steps', 'instruments', 'humidity'],
#             properties=dict(
#                 order=[
#                     "name",

#                     "temperature",
#                     "time",
#                     "function",
#                     "previous_process",
#                     "batch",
#                     "samples"])))


# class peroTF_TFL_BetaBox_ThermalAnnealing(ThermalAnnealing, EntryData):
#     m_def = Section(
#         a_eln=dict(
#             hide=[
#                 'lab_id', 'users', 'location', 'end_time',  'steps', 'instruments', 'humidity'],
#             properties=dict(
#                 order=[
#                     "name",

#                     "temperature",
#                     "time",
#                     "function",
#                     "previous_process",
#                     "batch",
#                     "samples"])))


# class peroTF_TFL_Fumehood_ThermalAnnealing(ThermalAnnealing, EntryData):
#     m_def = Section(
#         a_eln=dict(
#             hide=[
#                 'lab_id', 'users', 'location', 'end_time',  'steps', 'instruments', 'humidity'],
#             properties=dict(
#                 order=[
#                     "name",

#                     "temperature",
#                     "time",
#                     "function",
#                     "previous_process",
#                     "batch",
#                     "samples"])))


# %% ### Evaporation


class peroTF_TFL_SputterSystem_Sputtering(Sputtering, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'users', 'location', 'end_time',  'steps', 'instruments'],
            properties=dict(
                order=[
                    "name",
                    "present",
                    "datetime", "previous_process",
                    "batch",
                    "samples", "layer"])))


class peroTF_TFL_Ebeam_Evaporation(Evaporations, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'users', 'location', 'end_time',  'steps', 'instruments'],
            properties=dict(
                order=[
                    "name",
                    "present",
                    "datetime", "previous_process",
                    "batch",
                    "samples", "layer"])))


class peroTF_CR_Angstrom_Evaporation(Evaporations, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'users', 'location', 'end_time',  'steps', 'instruments'],
            properties=dict(
                order=[
                    "name",
                    "present",
                    "datetime", "previous_process",
                    "batch",
                    "samples", "layer"])))


class peroTF_TFL_BellJar_Evaporation(Evaporations, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'users', 'location', 'end_time',  'steps', 'instruments'],
            properties=dict(
                order=[
                    "name",
                    "present",
                    "datetime", "previous_process",
                    "batch",
                    "samples", "layer"])))


class peroTF_UP_PEROvap_Evaporation(Evaporations, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'users', 'location', 'end_time',  'steps', 'instruments'],
            properties=dict(
                order=[
                    "name",
                    "present",
                    "datetime", "previous_process",
                    "batch",
                    "samples", "layer"])))


class peroTF_TFL_PEROvap_Evaporation(Evaporations, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'users', 'location', 'end_time',  'steps', 'instruments'],
            properties=dict(
                order=[
                    "name",
                    "present",
                    "datetime", "previous_process",
                    "batch",
                    "samples", "layer"])))


class peroTF_UP_OPTIvap_Evaporation(Evaporations, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'users', 'location', 'end_time',  'steps', 'instruments'],
            properties=dict(
                order=[
                    "name",
                    "present",
                    "datetime", "previous_process",
                    "batch",
                    "samples", "layer"])))


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
                'end_time',  'steps', 'instruments', 'results',
                'certified_values',
                'certification_institute'],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "active_area",
                    "intensity",
                    "integration_time",
                    "settling_time",
                    "averaging",
                    "compliance",
                    "samples"])),
        a_plot=[
            {
                'x': 'jv_curve/:/voltage',
                'y': 'jv_curve/:/current_density',
                'layout': {
                    "showlegend": True,
                    'yaxis': {
                        "fixedrange": False},
                    'xaxis': {
                        "fixedrange": False}},
            }])

    multijunction_position = Quantity(
        type=str,
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=['top', 'mid', 'bottom'])
        ))

    def normalize(self, archive, logger):
        super(JVMeasurement, self).normalize(archive, logger)
        self.method = "JV Measurement"

        if self.data_file:
            from baseclasses.helper.utilities import get_encoding
            with archive.m_context.raw_file(self.data_file, "br") as f:
                encoding = get_encoding(f)

            with archive.m_context.raw_file(self.data_file, encoding=encoding) as f:
                from baseclasses.helper.file_parser.KIT_jv_parser import get_jv_data
                from baseclasses.helper.archive_builder.jv_archive import get_jv_archive

                jv_dict = get_jv_data(f.name, encoding)
                try:
                    self.datetime = convert_datetime(
                        jv_dict["datetime"], datetime_format="%Y-%m-%d %H:%M:%S", utc=False)
                    if not self.datetime:
                        self.datetime = convert_datetime(
                            jv_dict["datetime"], datetime_format="%Y-%m-%d %H:%M:%S %p", utc=False)
                except:
                    logger.warning("Couldnt parse datetime")

                get_jv_archive(jv_dict, self.data_file, self)

        super(peroTF_CR_SolSimBox_JVmeasurement,
              self).normalize(archive, logger)


class peroTF_CR_SolSimBox_MPPTracking(MPPTracking, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time',  'steps', 'instruments', 'results', ],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "samples"])),
        a_plot=[
            {
                'x': 'time',
                'y': ['efficiency', 'voltage'],
                'layout': {
                    "showlegend": True,
                    'yaxis': {
                        "fixedrange": False},
                    'xaxis': {
                        "fixedrange": False}},
            }])

    def normalize(self, archive, logger):
        if self.data_file:
            from baseclasses.helper.utilities import get_encoding
            with archive.m_context.raw_file(self.data_file, "br") as f:
                encoding = get_encoding(f)

            with archive.m_context.raw_file(self.data_file, encoding=encoding) as f:
                from baseclasses.helper.file_parser.KIT_mpp_parser import get_mpp_data, get_mpp_archive
                mpp_dict, data = get_mpp_data(f.name, encoding)
                get_mpp_archive(mpp_dict, data, self)
        super(peroTF_CR_SolSimBox_MPPTracking, self).normalize(archive, logger)


class peroTF_TFL_GammaBox_JVmeasurement(JVMeasurement, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time',  'steps', 'instruments', 'results',
                'certified_values',
                'certification_institute'],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "active_area",
                    "intensity",
                    "integration_time",
                    "settling_time",
                    "averaging",
                    "compliance",
                    "samples"])),
        a_plot=[
            {
                'x': 'jv_curve/:/voltage',
                'y': 'jv_curve/:/current_density',
                'layout': {
                    "showlegend": True,
                    'yaxis': {
                        "fixedrange": False},
                    'xaxis': {
                        "fixedrange": False}},
            }])

    multijunction_position = Quantity(
        type=str,
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=['top', 'mid', 'bottom'])
        ))

    def normalize(self, archive, logger):
        super(JVMeasurement, self).normalize(archive, logger)
        self.method = "JV Measurement"

        if self.data_file:
            from baseclasses.helper.utilities import get_encoding
            with archive.m_context.raw_file(self.data_file, "br") as f:
                encoding = get_encoding(f)

            with archive.m_context.raw_file(self.data_file, encoding=encoding) as f:
                from baseclasses.helper.file_parser.KIT_jv_parser import get_jv_data
                from baseclasses.helper.archive_builder.jv_archive import get_jv_archive

                jv_dict = get_jv_data(f.name, encoding)
                try:
                    self.datetime = convert_datetime(
                        jv_dict["datetime"], datetime_format="%Y-%m-%d %H:%M:%S %p", utc=False)
                    if not self.datetime:
                        self.datetime = convert_datetime(
                            jv_dict["datetime"], datetime_format="%Y-%m-%d %H:%M:%S", utc=False)
                except:
                    logger.warning("Couldnt parse datetime")
                get_jv_archive(jv_dict, self.data_file, self)

        super(peroTF_TFL_GammaBox_JVmeasurement,
              self).normalize(archive, logger)


class peroTF_TFL_GammaBox_EQEmeasurement(EQEMeasurement, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'users', 'location', 'end_time',  'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "samples"])))

    multijunction_position = Quantity(
        type=str,
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=['top', 'mid', 'bottom'])
        ))


# class peroTF_108_HyPrint_PLmeasurement(PLMeasurement, EntryData):
#     m_def = Section(
#         a_eln=dict(
#             hide=[
#                 'lab_id', 'users', 'location', 'end_time',  'steps', 'instruments', 'results']))


# class peroTF_1xx_nobox_UVvismeasurement(UVvisMeasurement, EntryData):
#     m_def = Section(
#         a_eln=dict(
#             hide=[
#                 'lab_id', 'users', 'location', 'end_time',  'steps', 'instruments', 'results']))

# %%####################################### Generic Entries


class peroTF_Process(BaseProcess, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'users', 'location', 'end_time'],
            properties=dict(
                order=[
                    "name",

                    "data_file",
                    "batch",
                    "samples"])))

    data_file = Quantity(
        type=str,
        shape=['*'],
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))


class peroTF_Deposition(LayerDeposition, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'users', 'location', 'end_time',  'instruments'],
            properties=dict(
                order=[
                    "name",

                    "layer_type",
                    "layer_material_name",
                    "layer_material",
                    "data_file",
                    "previous_process",
                    "batch",
                    "samples"])))

    data_file = Quantity(
        type=str,
        shape=['*'],
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))


class peroTF_WetChemicalDepoistion(WetChemicalDeposition, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time',  'instruments'],
            properties=dict(
                order=[
                    "name",
                    "present",
                    "datetime", "previous_process",
                    "batch",
                    "samples",
                    "solution",
                    "layer",
                    "quenching",
                    "annealing"])))

    data_file = Quantity(
        type=str,
        shape=['*'],
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))


class peroTF_Measurement(BaseMeasurement, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'users', 'location', 'end_time',  'instruments'],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "samples"])))

    data_file = Quantity(
        type=str,
        shape=['*'],
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))
