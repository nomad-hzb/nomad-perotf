from nomad.config.models.plugins import ParserEntryPoint


class PeroTFParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_perotf.parsers.perotf_measurement_parser import PeroTFParser

        return PeroTFParser(**self.dict())


# class HySprintExperimentParserEntryPoint(ParserEntryPoint):
#     def load(self):
#         from nomad_hysprint.parsers.hysprint_batch_parser import (
#             HySprintExperimentParser,
#         )

#         return HySprintExperimentParser(**self.dict())


perotf_parser = PeroTFParserEntryPoint(
    name='PeroTFParser',
    description='Parser for peroTF files',
    alias='perotf_parser',
    mainfile_name_re=r'^(.+\.?.+\.((eqe|jv|jvg|mpp|pero)\..{1,4}))$',
    mainfile_mime_re='(application|text|image)/.*',
)


# hysprint_experiment_parser = HySprintExperimentParserEntryPoint(
#     name='HySprintBatchParser',
#     description='Parser for Hysprint Batch xlsx files',
#     mainfile_name_re='^(.+\.xlsx)$',
#     # mainfile_contents_re='Experiment Info',
#     mainfile_mime_re='(application|text|image)/.*',
# )
