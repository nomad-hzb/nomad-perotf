from nomad.config.models.plugins import ParserEntryPoint


class PeroTFParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_perotf.parsers.perotf_measurement_parser import PeroTFParser

        return PeroTFParser(**self.dict())


class PeroTFExperimentParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_perotf.parsers.perotf_batch_parser import (
            PeroTFExperimentParser,
        )

        return PeroTFExperimentParser(**self.dict())


perotf_parser = PeroTFParserEntryPoint(
    name='PeroTFParser',
    description='Parser for peroTF files',
    alias='perotf_parser',
    mainfile_name_re=r'^(.+\.?.+\.((eqe|jv|mpp|pero)\..{1,4}))$',
    mainfile_mime_re='(application|text|image)/.*',
)


perotf_experiment_parser = PeroTFExperimentParserEntryPoint(
    name='PeroTFExperimentParser',
    description='Parser for perotf Batch xlsx files',
    mainfile_name_re='^(.+\.xlsx)$',
    # mainfile_contents_re='Experiment Info',
    mainfile_mime_re='(application|text|image)/.*',
)
