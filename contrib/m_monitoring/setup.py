import setuptools
from pathlib import Path


root_dir = Path(__file__).absolute().parent
with (root_dir / "VERSION").open() as f:
    version = f.read()
with (root_dir / "README.md").open() as f:
    long_description = f.read()
with (root_dir / "requirements.in").open() as f:
    requirements = f.read().splitlines()

module_name = "m_monitoring"

setuptools.setup(
    name=module_name,
    version=version,
    description="Sous module pour monitoring",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    maintainer="PNX",
    url="https://github.com/PNX-SI/gn_modulator/",
    packages=setuptools.find_packages("backend"),
    package_dir={"": "backend"},
    package_data={f"{module_name}.migrations": ["data/*.sql", "data/**/*.sql"]},
    install_requires=requirements,
    entry_points={
        "gn_module": [
            f"code = {module_name}:MODULE_CODE",
            f"picto = {module_name}:MODULE_PICTO",
            f"blueprint = {module_name}.blueprint:blueprint",
            f"migrations = {module_name}.migrations:versions",
            f"config_schema = {module_name}.conf_schema_toml:GnModuleSchemaConf",
        ]
    },
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3"
        "Operating System :: OS Independent",
    ],
)
