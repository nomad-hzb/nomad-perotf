# src/nomad_perotf/schema_packages/helpers.py

from nomad.datamodel.results import (
    BandGap,
    BandGapDeprecated,
    BandStructureElectronic,
    ElectronicProperties,
)

from nomad.datamodel.metainfo.common import ProvenanceTracker
import numpy as np
from nomad.units import ureg

def add_band_gap(archive, band_gaps):
    print('OUTPUT: ',band_gaps)
    if band_gaps is None:
        return

    if not isinstance(band_gaps, list):
        band_gaps = [band_gaps]

    band_gap_objects = []
    band_gap_deprecated_objects = []

    for gap in band_gaps:
        bg_depr = BandGapDeprecated(value=np.float64(gap) * ureg('eV'))
        bg = BandGap(
            value=np.float64(gap) * ureg('eV'),
            provenance=ProvenanceTracker(label='uvvis_measurement'),
        )
        band_gap_objects.append(bg)
        band_gap_deprecated_objects.append(bg_depr)

    band_structure = BandStructureElectronic(
        band_gap=band_gap_deprecated_objects
    )
    electronic = ElectronicProperties(
        band_structure_electronic=[band_structure],
        band_gap=band_gap_objects
    )

    archive.results.properties.electronic = electronic
