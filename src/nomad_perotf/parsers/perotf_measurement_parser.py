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

import datetime
import os

from baseclasses.helper.utilities import (
    create_archive,
    get_entry_id_from_file_name,
    get_reference,
    set_sample_reference,
)
from nomad.datamodel import EntryArchive
from nomad.datamodel.data import (
    EntryData,
)
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
)
from nomad.datamodel.metainfo.basesections import (
    Activity,
)
from nomad.metainfo import (
    Quantity,
)
from nomad.parsing import MatchingParser

from nomad_perotf.schema_packages.perotf_package import (
    SolarCellEQE,
    peroTF_AbsPLMeasurement,
    peroTF_JVmeasurement,
    peroTF_Measurement,
    peroTF_MPPTracking,
    peroTF_TFL_GammaBox_EQEmeasurement,
    peroTF_UVvisMeasurement,
)  # its the copied one from FAIRMAT

"""
This is a hello world style example for an example parser/converter.
"""


class RawFileperoTF(EntryData):
    processed_archive = Quantity(
        type=Activity,
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
        ),
    )


class PeroTFParser(MatchingParser):
    def parse(self, mainfile: str, archive: EntryArchive, logger):
        # Log a hello world, just to get us started. TODO remove from an actual parser.

        mainfile_split = os.path.basename(mainfile).split('.')
        archive.data = RawFileperoTF()
        notes = ''
        if len(mainfile_split) > 2:
            notes = mainfile_split[1]
        entry = peroTF_Measurement()
        if mainfile_split[-2] == 'jv':
            if 'rev' in mainfile:
                return
            entry = peroTF_JVmeasurement()

        if mainfile_split[-1] == 'dat' and mainfile_split[-2] == 'eqe':
            # Bentham EQE system
            header_lines = 63
            sc_eqe = SolarCellEQE()
            sc_eqe.eqe_data_file = os.path.basename(mainfile)
            sc_eqe.header_lines = header_lines
            entry = peroTF_TFL_GammaBox_EQEmeasurement()
            entry.eqe_data = [sc_eqe]

        if mainfile_split[-1] == 'txt' and mainfile_split[-2] == 'eqe':
            # Enlitec EQE system
            header_lines = 5
            sc_eqe = SolarCellEQE()
            sc_eqe.eqe_data_file = os.path.basename(mainfile)
            sc_eqe.header_lines = header_lines
            entry = peroTF_TFL_GammaBox_EQEmeasurement()
            entry.eqe_data = [sc_eqe]

        if mainfile_split[-1] in ['csv', 'txt'] and mainfile_split[-2] == 'mpp':
            entry = peroTF_MPPTracking()
        if mainfile_split[-1] in ['csv'] and mainfile_split[-2] == 'uvvis':
            entry = peroTF_UVvisMeasurement()
        if (
            mainfile_split[-2] in ['jv', 'eqe', 'jvg', 'jvt']
            and len(mainfile_split) > 2
        ):
            if 'top' in mainfile_split[1]:
                entry.multijunction_position = 'top'
            if 'mid' in mainfile_split[1]:
                entry.multijunction_position = 'mid'
            if 'bot' in mainfile_split[1]:
                entry.multijunction_position = 'bottom'
        if mainfile_split[-1] in ['txt'] and mainfile_split[-2] == 'abspl':
            entry = peroTF_AbsPLMeasurement()

        archive.metadata.entry_name = os.path.basename(mainfile)
        search_id = mainfile_split[0]
        set_sample_reference(archive, entry, search_id)

        entry.name = f'{search_id} {notes}'
        entry.description = f'Notes from file name: {notes}'
        entry.datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        if not mainfile_split[-2] == 'eqe' and not mainfile_split[-2] == 'uvvis':
            entry.data_file = os.path.basename(mainfile)
        elif mainfile_split[-2] == 'uvvis':
            entry.data_file = [os.path.basename(mainfile)]
            print(entry.data_file)
            entry.datetime = None

        file_name = f'{os.path.basename(mainfile)}.archive.json'
        eid = get_entry_id_from_file_name(file_name, archive)
        archive.data = RawFileperoTF(
            processed_archive=get_reference(archive.metadata.upload_id, eid)
        )
        create_archive(entry, archive, file_name)
