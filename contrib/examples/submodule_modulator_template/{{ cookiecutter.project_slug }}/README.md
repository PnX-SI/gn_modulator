# {{cookiecutter.project_name}}

{{cookiecutter.project_description}}

## Setup

Be sure to have `gn_modulator` installed in your Geonature instance. If not, refer to [https://github.com/PnX-SI/gn_modulator](https://github.com/PnX-SI/gn_modulator).

To install {{cookiecutter.module_name}}, run the following command.

```shell
source <pathtogeonature>/backend/venv/bin/activate
geonature modulator install -p {{cookiecutter.module_name}}
```

**Reminder** As every module in GeoNature, be sure that your user(s) have necessary permissions to access your module.