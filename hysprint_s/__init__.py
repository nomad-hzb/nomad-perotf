#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import random
import string
import numpy as np

# from nomad.units import ureg
from nomad.metainfo import (
    Package,
    Quantity,
    SubSection,
    Section)

from nomad.datamodel.data import EntryData
from nomad.datamodel.results import Results, Properties, Material, ELN

from baseclasses import (
    ProcessOnSample, MeasurementOnSample, LayerDeposition, Batch
)

from baseclasses.chemical import (
    Chemical
)

from baseclasses.characterizations import (
    XRD
)

from baseclasses.solution import Solution, Ink
from baseclasses.experimental_plan import ExperimentalPlan

from baseclasses.wet_chemical_deposition import (
    SpinCoating,
    SpinCoatingRecipe,
    SlotDieCoating,
    InkjetPrinting,
    VaporizationAndDropCasting,
    SprayPyrolysis)

from baseclasses.vapour_based_deposition import (
    Evaporations)

from baseclasses.material_processes_misc import (
    Cleaning,
    SolutionCleaning,
    PlasmaCleaning,
    UVCleaning,
    ThermalAnnealing,
    Storage)

from baseclasses.solar_energy import (
    StandardSampleSolarCell,
    Substrate,
    TimeResolvedPhotoluminescence,
    JVMeasurement,
    PLMeasurement,
    UVvisMeasurement,
    EQEMeasurement,
    OpticalMicroscope,
    SolcarCellSample, BasicSampleWithID
)

from baseclasses.chemical_energy import (
    Electrode, Electrolyte, ElectroChemicalCell
)

from baseclasses.chemical_energy import (
    CyclicVoltammetry)


m_package0 = Package(name='HySprint')

# %% ####################### Entities


def randStr(chars=string.ascii_uppercase + string.digits, N=6):
    return ''.join(random.choice(chars) for _ in range(N))


class HySprint_ExperimentalPlan(ExperimentalPlan, EntryData):
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
        a_template=dict(institute="HZB_Hysprint"))

    def normalize(self, archive, logger):
        super(HySprint_ExperimentalPlan, self).normalize(archive, logger)
        if not (self.standard_plan and self.number_of_substrates > 0
                and self.number_of_substrates % self.substrates_per_subbatch == 0
                and self.plan and self.standard_plan.processes):
            return

        from baseclasses.helper.execute_solar_sample_plan import execute_solar_sample_plan
        execute_solar_sample_plan(
            self, archive, HySprint_Sample, HySprint_Batch)

        # actual normalization!!
        archive.results = Results()
        archive.results.properties = Properties()
        archive.results.material = Material()
        archive.results.eln = ELN()
        archive.results.eln.sections = ["HySprint_ExperimentalPlan"]


class HySprint_StandardSample(StandardSampleSolarCell, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['users'],
            properties=dict(
                order=[
                    "name",
                    "architecture",
                    "substrate",
                    "processes",
                    "lab_id"
                ])))


class HySprint_SpinCoating_Recipe(SpinCoatingRecipe, EntryData):
    m_def = Section(
        a_eln=dict(hide=['lab_id', 'users']))


class HySprint_Chemical(Chemical, EntryData):
    m_def = Section(
        a_eln=dict(hide=['lab_id', 'users']))


class Hysprint_Electrode(Electrode, EntryData):
    m_def = Section(
        a_eln=dict(hide=['users', 'origin'],
                   properties=dict(
            order=[
                "name", "lab_id",
                "chemical_composition_or_formulas"
            ]))
    )


class Hysprint_Electrolyte(Electrolyte, EntryData):
    m_def = Section(
        a_eln=dict(hide=['users', 'origin'],
                   properties=dict(
            order=[
                "name", "lab_id", "chemical_composition_or_formulas"
            ]))
    )


class Hysprint_ElectroChemicalCell(ElectroChemicalCell, EntryData):
    m_def = Section(
        a_eln=dict(hide=['users', 'origin'],
                   properties=dict(
            order=[
                "name",
                "lab_id",
                "chemical_composition_or_formulas",
                "working_electrode",
                "reference_electrode",
                "counter_electrode",
                "electrolyte"
            ])),
    )


class HySprint_Substrate(Substrate, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users'],
            properties=dict(
                order=[
                    "name",
                    "substrate",
                    "conducting_material",
                    "solar_cell_area",
                    "pixel_area",
                    "number_of_pixels"])))


class HySprint_Solution(Solution, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users'],
            properties=dict(
                order=[
                    "name",
                    "method",
                    "temperature",
                    "time",
                    "speed",
                    "solvent_ratio"])),
        a_template=dict(
            temperature=45,
            time=15,
            method='Shaker'))


class HySprint_Ink(Ink, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'chemical_formula'],
            properties=dict(
                order=[
                    "name",
                    "method",
                    "temperature",
                    "time",
                    "speed",
                    "solvent_ratio"])),
        a_template=dict(
            temperature=45,
            time=15,
            method='Shaker'))


class HySprint_Sample(SolcarCellSample, EntryData):
    m_def = Section(
        a_eln=dict(hide=['users'], properties=dict(
            order=["name", "substrate", "architecture"])),
        a_template=dict(institute="HZB_Hysprint"),
        label_quantity='sample_id'
    )


class HySprint_BasicSample(BasicSampleWithID, EntryData):
    m_def = Section(
        a_eln=dict(hide=['users']),
        a_template=dict(institute="HZB_Hysprint"),
        label_quantity='sample_id'
    )


class HySprint_Batch(Batch, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['users'],
            properties=dict(
                order=[
                    "name",
                    "samples",
                    "export_batch_ids",
                    "csv_export_file"])))


class HySprint_BasicBatch(Batch, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['users'],
            properties=dict(
                order=[
                    "name",
                    "samples",
                    "number_of_samples",
                    "create_samples",
                    "export_batch_ids",
                    "csv_export_file"])))

    number_of_samples = Quantity(
        type=np.dtype(np.int64),
        default=0,
        a_eln=dict(
            component='NumberEditQuantity'
        ))

    create_samples = Quantity(
        type=bool,
        default=False,
        a_eln=dict(component='BoolEditQuantity')
    )

    def normalize(self, archive, logger):
        super(HySprint_BasicBatch, self).normalize(archive, logger)

        if self.number_of_samples > 0 and self.create_samples:
            self.create_samples = False
            samples = []
            from baseclasses.helper.execute_solar_sample_plan import create_archive, get_entry_id_from_file_name, get_reference
            sample_name_id = self.batch_id.sample_short_name if self.batch_id is not None else None
            for sample_idx in range(self.number_of_samples):
                hysprint_basicsample = HySprint_BasicSample(
                    sample_id=self.batch_id if self.batch_id is not None else None,
                    datetime=self.datetime if self.datetime is not None else None,
                    description=self.description if self.description is not None else None,
                    name=f'{self.name} {sample_idx}' if self.name is not None else None,
                )
                hysprint_basicsample.sample_id.sample_short_name = f'{sample_name_id}_{sample_idx}'

                file_name = f'{self.name.replace(" ","_")}_{sample_idx}.archive.json'
                create_archive(hysprint_basicsample, archive, file_name)
                if sample_name_id is not None:
                    self.batch_id.sample_short_name = sample_name_id
                entry_id = get_entry_id_from_file_name(file_name, archive)

                samples.append(get_reference(
                    archive.metadata.upload_id, entry_id))
            self.samples = []
            self.samples = samples

# %% ####################### Cleaning


class HySprint_114_SolventFumeHood_Cleaning(Cleaning, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time'],
            properties=dict(
                order=[
                    "name",
                    "is_standard_process",
                    "datetime", "previous_process",
                    "batch",
                    "samples"])))

    cleaning = SubSection(
        section_def=SolutionCleaning, repeats=True)


class IRIS_2031_Printerlab_SolutionCleaning(Cleaning, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time'],
            properties=dict(
                order=[
                    "name",
                    "is_standard_process",
                    "datetime", "previous_process",
                    "batch",
                    "samples"])))

    cleaning = SubSection(
        section_def=SolutionCleaning, repeats=True)


class IRIS_2135_Preparationlab_SolutionCleaning(Cleaning, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time'],
            properties=dict(
                order=[
                    "name",
                    "is_standard_process",
                    "datetime", "previous_process",
                    "batch",
                    "samples"])))

    cleaning = SubSection(
        section_def=SolutionCleaning, repeats=True)


class HySprint_114_HyFlowBox_Cleaning_UV(Cleaning, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time'],
            properties=dict(
                order=[
                    "name",
                    "is_standard_process",
                    "datetime", "previous_process",
                    "batch",
                    "samples"])))

    cleaning = SubSection(
        section_def=UVCleaning, repeats=True)


class IRIS_2031_Printerlab_Cleaning_UV(Cleaning, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time'],
            properties=dict(
                order=[
                    "name",
                    "is_standard_process",
                    "datetime", "previous_process",
                    "batch",
                    "samples"])))

    cleaning = SubSection(
        section_def=UVCleaning, repeats=True)


class HySprint_114_HyFlowBox_Cleaning_Plasma(Cleaning, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time'],
            properties=dict(
                order=[
                    "name",
                    "is_standard_process",
                    "datetime", "previous_process",
                    "batch",
                    "samples"])))

    cleaning = SubSection(
        section_def=PlasmaCleaning, repeats=True)


class IRIS_2135_Preparationlab_Cleaning_Plasma(Cleaning, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time'],
            properties=dict(
                order=[
                    "name",
                    "is_standard_process",
                    "datetime", "previous_process",
                    "batch",
                    "samples"])))

    cleaning = SubSection(
        section_def=PlasmaCleaning, repeats=True)


# %% ##################### Layer Deposition


class HySprint_114_HTFumeHood_SprayPyrolysis(SprayPyrolysis, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time'],
            properties=dict(
                order=[
                    "name",
                    "is_standard_process",
                    "layer_type",
                    "layer_material_name",
                    "layer_material",
                    "datetime", "previous_process",
                    "batch",
                    "samples"])))

# %% ### Dropcasting


class HySprint_VaporizationAndDropCasting(
        VaporizationAndDropCasting, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time',
                'previous_process'],
            properties=dict(
                order=[
                    "name",
                    "is_standard_process",
                    "layer_type",
                    "layer_material_name",
                    "layer_material",
                    "batch",
                    "samples"])),
        a_template=dict(
            layer_type="Non-functional layer",
        ))

# %% ### Printing


class IRIS_2038_HZBGloveBoxes_Pero3Inkjet_Inkjet_Printing(
        InkjetPrinting, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time'],
            properties=dict(
                order=[
                    "name",
                    "is_standard_process",
                    "layer_type",
                    "layer_material_name",
                    "layer_material",
                    "recipe_used",
                    "print_head_used",
                    "ink",
                    "datetime",
                    "previous_process",
                    "batch",
                    "samples"])),
        a_template=dict(
            layer_type="Absorber Layer",
        ))


# %% ### Spin Coating

class HySprint_114_HyFlowBox_SpinCoating(SpinCoating, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time'],
            properties=dict(
                order=[
                    "name",
                    "is_standard_process",
                    "layer_type",
                    "layer_material_name",
                    "layer_material",
                    "recipe",
                    "datetime", "previous_process",
                    "batch",
                    "samples"])),
        a_template=dict(
            layer_type="Absorber Layer",
        ))


class HySprint_108_HyPeroSpin_SpinCoating(SpinCoating, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time'],
            properties=dict(
                order=[
                    "name",
                    "is_standard_process",
                    "layer_type",
                    "layer_material_name",
                    "layer_material",
                    "recipe",
                    "datetime", "previous_process",
                    "batch",
                    "samples"])),
        a_template=dict(
            layer_type="Absorber Layer",
        ))


class IRIS_2038_HZBGloveBoxes_Pero2Spincoater_SpinCoating(
        SpinCoating, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time'],
            properties=dict(
                order=[
                    "name",
                    "is_standard_process",
                    "layer_type",
                    "layer_material_name",
                    "layer_material",
                    "recipe",
                    "datetime", "previous_process",
                    "batch",
                    "samples"])),
        a_template=dict(
            layer_type="Absorber Layer",
        ))


class HySprint_108_HySpin_SpinCoating(SpinCoating, EntryData):

    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time'],
            properties=dict(
                order=[
                    "name",
                    "is_standard_process",
                    "layer_type",
                    "layer_material_name",
                    "layer_material",
                    "recipe",
                    "datetime", "previous_process",
                    "batch",
                    "samples"])))


class HySprint_104_ProtoVap_SpinCoating(SpinCoating, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'author',
                'end_time'],
            properties=dict(
                order=[
                    "name",
                    "is_standard_process",
                    "layer_type",
                    "layer_material_name",
                    "layer_material",
                    "recipe",
                    "datetime", "previous_process",
                    "batch",
                    "samples"])),
        a_template=dict(
            layer_type="Absorber Layer"))

# %% ### Slot Die Coating


class HySprint_108_HySDC_SlotDieCoating(SlotDieCoating, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'author',
                'end_time'],
            properties=dict(
                order=[
                    "name",
                    "is_standard_process",
                    "layer_type",
                    "layer_material_name",
                    "layer_material",
                    "datetime", "previous_process",
                    "batch",
                    "samples"])),
        a_template=dict(
            layer_type="Absorber Layer"))


# %% ### Annealing

class HySprint_108_HyPeroSpin_ThermalAnnealing(ThermalAnnealing, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time',
                'humidity'],
            properties=dict(
                order=[
                    "name",
                    "is_standard_process",
                    "temperature",
                    "time",
                    "function",
                    "datetime", "previous_process",
                    "batch",
                    "samples"])))


class HySprint_108_HySpin_ThermalAnnealing(ThermalAnnealing, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time',
                'humidity'],
            properties=dict(
                order=[
                    "name",
                    "is_standard_process",
                    "temperature",
                    "time",
                    "function",
                    "datetime", "previous_process",
                    "batch",
                    "samples"])))


class HySprint_108_HyCDABox_ThermalAnnealing(ThermalAnnealing, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time'],
            properties=dict(
                order=[
                    "name",
                    "is_standard_process",
                    "temperature",
                    "time",
                    "function",
                    "datetime", "previous_process",
                    "batch",
                    "samples"])))


class HySprint_108_HySDC_ThermalAnnealing(ThermalAnnealing, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time',
                'humidity'],
            properties=dict(
                order=[
                    "name",
                    "is_standard_process",
                    "temperature",
                    "time",
                    "function",
                    "datetime", "previous_process",
                    "batch",
                    "samples"])))


class HySprint_104_ProtoVap_ThermalAnnealing(ThermalAnnealing, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time',
                'humidity'],
            properties=dict(
                order=[
                    "name",
                    "is_standard_process",
                    "temperature",
                    "time",
                    "function",
                    "datetime", "previous_process",
                    "batch",
                    "samples"])))

# %% ### Evaporation


class IRIS_2038_HZBGloveBoxes_Pero5Evaporation_Evaporation(
        Evaporations, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time'],
            properties=dict(
                order=[
                    "name",
                    "is_standard_process",
                    "layer_type",
                    "layer_material_name",
                    "layer_material",
                    "datetime", "previous_process",
                    "batch",
                    "samples"])))


class HySprint_108_HyVap_Evaporation(Evaporations, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time'],
            properties=dict(
                order=[
                    "name",
                    "is_standard_process",
                    "layer_type",
                    "layer_material_name",
                    "layer_material",
                    "datetime", "previous_process",
                    "batch",
                    "samples"])))


class HySprint_108_HyPeroVap_Evaporation(Evaporations, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time'],
            properties=dict(
                order=[
                    "name",
                    "is_standard_process",
                    "layer_type",
                    "layer_material_name",
                    "layer_material",
                    "datetime", "previous_process",
                    "batch",
                    "samples"])))


class HySprint_104_ProtoVap_Evaporation(Evaporations, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time'],
            properties=dict(
                order=[
                    "name",
                    "is_standard_process",
                    "layer_type",
                    "layer_material_name",
                    "layer_material",
                    "datetime", "previous_process",
                    "batch",
                    "samples"])))
# %% ## Storage


class HySprint_108_HyDryAir_Storage(Storage, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time'],
            properties=dict(
                order=[
                    "name",
                    "is_standard_process",
                    "datetime", "previous_process",
                    "batch",
                    "samples"])))


# %%####################################### Measurements

class Wannsee_B307_CyclicVoltammetry_CorrWare(CyclicVoltammetry, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                "location",
                "end_time",
                "metadata_file"],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "working_electrode",
                    "reference_electrode",
                    "counter_electrode",
                    "electrolyte",
                    "electrochemical_cell",
                    "samples"])),
        a_plot=[
            {
                'x': 'cycles/:/voltage',
                'y': 'cycles/:/current_density',
                'layout': {
                    "showlegend": True,
                    'yaxis': {
                        "fixedrange": False},
                    'xaxis': {
                        "fixedrange": False}},
            }])


class Wannsee_B307_CyclicVoltammetry_ECLab(CyclicVoltammetry, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                "location",
                "end_time",
                "metadata_file"],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "working_electrode",
                    "reference_electrode",
                    "counter_electrode",
                    "electrolyte",
                    "electrochemical_cell",
                    "samples"])),
        a_plot=[
            {
                'x': 'cycles/:/voltage',
                'y': 'cycles/:/current',
                'layout': {
                    "showlegend": True,
                    'yaxis': {
                        "fixedrange": False},
                    'xaxis': {
                        "fixedrange": False}},
            }])


class HySprint_108_HyVap_JVmeasurement(JVMeasurement, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'author',
                'certified_values',
                'certification_institute',
                'end_time',
                'location'],
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


class IRIS_2038_HZBGloveBoxes_Pero4SOSIMStorage_JVmeasurement(
        JVMeasurement, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'author',
                'certified_values',
                'certification_institute',
                'end_time',
                'location'],
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


class HySprint_TimeResolvedPhotoluminescence(
        TimeResolvedPhotoluminescence, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'author',
                'certified_values',
                'certification_institute',
                'location',
                'end_time'],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "samples"])),
        a_plot=[
            {
                'x': 'trpl_properties/:/time',
                'y': 'trpl_properties/:/counts',
                'layout': {
                    "showlegend": True,
                    'yaxis': {
                        "fixedrange": False,
                        'type': 'log'},
                    'xaxis': {
                        "fixedrange": False}},
            }])


class HySprint_OpticalMicroscope(
        OpticalMicroscope, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'author',
                'detector_data_folder',
                'external_sample_url',
                'location',
                'end_time'],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "samples"])),
    )


class HySprint_108_HyVap_EQEmeasurement(EQEMeasurement, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time'],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "samples"])),
        a_plot=[
            {
                'x': 'eqe_data/:/photon_energy_array',
                'y': 'eqe_data/:/eqe_array',
                'layout': {
                    "showlegend": True,
                    'yaxis': {
                        "fixedrange": False},
                    'xaxis': {
                        "fixedrange": False}},
            }])


class HySprint_108_HyPrint_PLmeasurement(PLMeasurement, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time'],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "samples"])))


class IRIS_2038_HZBGloveBoxes_Pero2Spincoater_PLMeasurment(
        PLMeasurement, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time'],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "samples"])))


class HySprint_1xx_nobox_UVvismeasurement(UVvisMeasurement, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time'],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "samples"])))


class IRIS_2038_HZBGloveBoxes_Pero2Spincoater_UVvis(
        UVvisMeasurement, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time'],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "samples"])))


class Wannsee_D8_XRD_Bruker(XRD, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                "location",
                "end_time",
                "metadata_file",
                "shifted_data",
                "identifier"],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "samples"])),
        a_plot=[
            {
                'x': [
                    'measurements/:/angle',
                    'shifted_data/:/angle'],
                'y': [
                    'measurements/:/intensity',
                    'shifted_data/:/intensity'],
                'layout': {
                    'yaxis': {
                        "fixedrange": False,
                        "title": "Counts"},
                    'xaxis': {
                        "fixedrange": False}}},
        ])

    def normalize(self, archive, logger):
        self.identifier = "HZB_WANNSEE"
        super(Wannsee_D8_XRD_Bruker, self).normalize(archive, logger)

# %%####################################### Generic Entries


class HySprint_Process(ProcessOnSample, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time'],
            properties=dict(
                order=[
                    "name",
                    "is_standard_process",
                    "data_file",
                    "batch",
                    "samples"])))

    data_file = Quantity(
        type=str,
        shape=['*'],
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))


class HySprint_Deposition(LayerDeposition, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time'],
            properties=dict(
                order=[
                    "name",
                    "is_standard_process",
                    "layer_type",
                    "layer_material_name",
                    "layer_material",
                    "data_file",
                    "datetime", "previous_process",
                    "batch",
                    "samples"])))

    data_file = Quantity(
        type=str,
        shape=['*'],
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))


class HySprint_Measurement(MeasurementOnSample, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time'],
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
