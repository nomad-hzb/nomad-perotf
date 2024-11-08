from nomad.config.models.plugins import SchemaPackageEntryPoint


class PeroTFPackageEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from nomad_perotf.schema_packages.perotf_package import m_package

        return m_package


perotf_package = PeroTFPackageEntryPoint(
    name='PeroTF',
    description='Package for perotf Lab',
)
