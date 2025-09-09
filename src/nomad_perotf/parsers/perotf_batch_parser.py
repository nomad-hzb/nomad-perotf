#!/usr/bin/env python3
"""
Created on Fri Sep 27 09:08:03 2024

@author: a2853
"""

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

import pandas as pd
from baseclasses.helper.solar_cell_batch_mapping import (
    get_reference,
    map_annealing_class,
    map_atomic_layer_deposition,
    map_basic_sample,
    map_batch,
    map_cleaning,
    map_close_space_sublimation,
    map_dip_coating,
    map_evaporation,
    map_generic,
    map_inkjet_printing,
    map_sdc,
    map_spin_coating,
    map_sputtering,
    map_substrate,
)
from baseclasses.helper.utilities import create_archive
from nomad.datamodel import EntryArchive
from nomad.datamodel.data import (
    EntryData,
)
from nomad.datamodel.metainfo.basesections import (
    Entity,
)
from nomad.metainfo import (
    Quantity,
)
from nomad.parsing import MatchingParser

from nomad_perotf.schema_packages.perotf_package import (
    peroTF_ALD,
    peroTF_Batch,
    peroTF_Cleaning,
    peroTF_CloseSpaceSublimation,
    peroTF_DipCoating,
    peroTF_Evaporation,
    peroTF_InkjetPrinting,
    peroTF_Process,
    peroTF_Sample,
    peroTF_SlotDieCoating,
    peroTF_SpinCoating,
    peroTF_Sputtering,
    peroTF_Substrate,
    peroTF_ThermalAnnealing,
)


class RawHySprintExperiment(EntryData):
    processed_archive = Quantity(type=Entity, shape=['*'])


class PeroTFExperimentParser(MatchingParser):
    def is_mainfile(
        self,
        filename: str,
        mime: str,
        buffer: bytes,
        decoded_buffer: str,
        compression: str = None,
    ):
        is_mainfile_super = super().is_mainfile(
            filename, mime, buffer, decoded_buffer, compression
        )
        if not is_mainfile_super:
            return False
        try:
            df = pd.read_excel(filename, header=[0, 1])
            df['Experiment Info']['Nomad ID'].dropna().to_list()
        except Exception:
            return False
        return True

    def parse(self, mainfile: str, archive: EntryArchive, logger):
        upload_id = archive.metadata.upload_id
        # xls = pd.ExcelFile(mainfile)
        df = pd.read_excel(mainfile, header=[0, 1])
        df = df[~df['Experiment Info']['Nomad ID'].isna()]
        sample_ids = df['Experiment Info']['Nomad ID'].dropna().to_list()
        batch_id = '_'.join(sample_ids[0].split('_')[:-1])
        archives = [map_batch(sample_ids, batch_id, upload_id, peroTF_Batch)]
        substrates = []
        substrates_col = [
            'Sample dimension',
            'Sample area [cm^2]',
            'Substrate material',
            'Substrate conductive layer',
            'Notes',
            'Bottom Cell Name',
        ]
        substrates_col = [
            s for s in substrates_col if s in df['Experiment Info'].columns
        ]
        for i, sub in (
            df['Experiment Info'][substrates_col].drop_duplicates().iterrows()
        ):
            if pd.isna(sub).all():
                continue
            substrates.append(
                (f'{i}_substrate', sub, map_substrate(sub, peroTF_Substrate))
            )

        def find_substrate(d):
            for s in substrates:
                if d.equals(s[1]):
                    return s[0]

        for i, row in df['Experiment Info'].iterrows():
            if pd.isna(row).all():
                continue
            substrate_name = find_substrate(row[substrates_col]) + '.archive.json'
            archives.append(
                map_basic_sample(row, substrate_name, upload_id, peroTF_Sample)
            )

        for i, col in enumerate(df.columns.get_level_values(0).unique()):
            if col == 'Experiment Info':
                continue

            df_dropped = df[col].drop_duplicates()
            for j, row in df_dropped.iterrows():
                if row.isnull().all():
                    continue
                lab_ids = [
                    x['Experiment Info']['Nomad ID']
                    for _, x in df[['Experiment Info', col]].iterrows()
                    if x[col].astype('object').equals(row.astype('object'))
                ]
                if 'Cleaning' in col:
                    archives.append(
                        map_cleaning(i, j, lab_ids, row, upload_id, peroTF_Cleaning)
                    )

                # if 'Laser Scribing' in col:
                #     archives.append(map_laser_scribing(i, j, lab_ids, row, upload_id))

                if 'Generic Process' in col:  # move up
                    archives.append(
                        map_generic(i, j, lab_ids, row, upload_id, peroTF_Process)
                    )

                if 'Annealing' in col:  # move up
                    archives.append(
                        map_annealing_class(
                            i, j, lab_ids, row, upload_id, peroTF_ThermalAnnealing
                        )
                    )

                if pd.isna(row.get('Material name')):
                    continue

                if 'Evaporation' in col:
                    coevaporation = False
                    if 'Co-Evaporation' in col:
                        coevaporation = True
                    archives.append(
                        map_evaporation(
                            i,
                            j,
                            lab_ids,
                            row,
                            upload_id,
                            peroTF_Evaporation,
                            coevaporation,
                        )
                    )

                if 'Close Space Sublimation' in col:
                    archives.append(
                        map_close_space_sublimation(
                            i, j, lab_ids, row, upload_id, peroTF_CloseSpaceSublimation
                        )
                    )

                if 'Spin Coating' in col:
                    archives.append(
                        map_spin_coating(
                            i, j, lab_ids, row, upload_id, peroTF_SpinCoating
                        )
                    )

                if 'Inkjet Printing' in col:
                    archives.append(
                        map_inkjet_printing(
                            i, j, lab_ids, row, upload_id, peroTF_InkjetPrinting
                        )
                    )

                if 'Dip Coating' in col:
                    archives.append(
                        map_dip_coating(
                            i, j, lab_ids, row, upload_id, peroTF_DipCoating
                        )
                    )

                if 'Slot Die Coating' in col:
                    archives.append(
                        map_sdc(i, j, lab_ids, row, upload_id, peroTF_SlotDieCoating)
                    )

                if 'Sputtering' in col:
                    archives.append(
                        map_sputtering(i, j, lab_ids, row, upload_id, peroTF_Sputtering)
                    )

                if 'ALD' in col:
                    archives.append(
                        map_atomic_layer_deposition(
                            i, j, lab_ids, row, upload_id, peroTF_ALD
                        )
                    )

        refs = []
        for subs in substrates:
            file_name = f'{subs[0]}.archive.json'
            create_archive(subs[2], archive, file_name)
            refs.append(get_reference(upload_id, file_name))

        for a in archives:
            file_name = f'{a[0]}.archive.json'
            create_archive(a[1], archive, file_name)
            refs.append(get_reference(upload_id, file_name))

        archive.data = RawHySprintExperiment(processed_archive=refs)
