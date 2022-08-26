import { Injectable, Injector } from "@angular/core";

import { HttpClient } from "@angular/common/http";

import { Observable, Subject, of } from "@librairies/rxjs";
import { mergeMap, concatMap } from "@librairies/rxjs/operators";

import { CommonService } from "@geonature_common/service/common.service";
import { ModulesDataService } from "./data.service";
import { ModulesFormService } from "./form.service";
import { ModulesConfigService } from "./config.service";
import { ModulesLayoutService } from "./layout.service";

@Injectable()
export class ModulesSchemaService {
  private _cache = {};

  _mData: ModulesDataService;
  _mForm: ModulesFormService;
  _mConfig: ModulesConfigService;
  _mLayout: ModulesLayoutService;

  constructor(private _injector: Injector) {
    this._mData = this._injector.get(ModulesDataService);
    this._mForm = this._injector.get(ModulesFormService);
    this._mConfig = this._injector.get(ModulesConfigService);
    this._mLayout = this._injector.get(ModulesLayoutService);
  }

  processFormLayout(schemaConfig) {
    const schemaLayout = schemaConfig.form.layout;
    return {
      type: "form",
      appearance: "fill",
      direction: "row",
      items: [
        {
          type: "map",
          key: schemaConfig.utils.geometry_field_name,
          edit: true,
          gps: true,
          hidden: !schemaConfig?.utils.geometry_field_name,
          flex: schemaConfig?.utils.geometry_field_name ? '1': '0'
        },
        {
          items: [
            {
              title: [
                "__f__{",
                `  const id = data.${schemaConfig.utils.pk_field_name};`,
                "  return id",
                "    ? `Modification " +
                  schemaConfig.display.du_label +
                  " ${data." +
                  schemaConfig.utils.label_field_name +
                  "}`",
                `    : "Création ${schemaConfig.display.un_nouveau_label}";`,
                "}",
              ],
              flex: "0",
            },
            {
              flex: "0",
              type: "message",
              html: "Veuillez saisir une geometrie sur la carte",
              class: "error",
              hidden: `__f__(!${schemaConfig.utils.geometry_field_name}) || data.${schemaConfig.utils.geometry_field_name}?.coordinates`,
            },
            {
              items: schemaLayout,
              overflow: true,
            },
            {
              flex: "0",
              direction: "row",
              items: [
                {
                  flex: "initial",
                  type: "button",
                  color: "primary",
                  title: "Valider",
                  description: "Enregistrer le contenu du formulaire",
                  action: "submit",
                  disabled: "__f__!(formGroup.valid )",
                },
                {
                  flex: "initial",
                  type: "button",
                  color: "primary",
                  title: "Annuler",
                  description: "Annuler l'édition",
                  action: "cancel",
                },
              ],
            },
          ],
        },
      ],
    };
  }

  processPropertiesLayout(schemaConfig, moduleConfig) {
    return {
      // height_auto: true,
      direction: "row",
      items: [
        // {
        //   type: "map",
        //   key: schemaConfig.utils.geometry_field_name,
        // },
        {
          items: [
            {
              title: `__f__'Propriétés ${schemaConfig.display.du_label} ' + data.${schemaConfig.utils.label_field_name}`,
              flex: "0",
            },
            {
              items: schemaConfig.details.layout,
              overflow: true,
            },
            {
              type: "button",
              color: "primary",
              title: "Éditer",
              description: `Editer ${schemaConfig.display.le_label}`,
              action: "edit",
              hidden: `__f__data.cruved_ownership > ${moduleConfig.module.cruved["U"]}`,
              flex: "0",
            },
          ],
        },
      ],
    };
  }

  onSubmit(schemaName, data, layout) {
    if (!data) {
      return;
    }

    const fields = this.getFields(schemaName, layout);

    const processedData = this._mForm.processData(data, layout);

    const request = this.id(schemaName, data)
      ? this._mData.patch(
          schemaName,
          this.id(schemaName, data),
          processedData,
          {
            fields,
          }
        )
      : this._mData.post(schemaName, processedData, {
          fields,
        });

    return request;
  }

  getFields(schemaName, layout) {
    const fields = this._mLayout.getLayoutFields(layout);

    if (this.geometryFieldName(schemaName) && this.geometryFieldName(schemaName)) {
      fields.push(this.geometryFieldName(schemaName));
    }

    if (!fields.includes(this.pkFieldName(schemaName))) {
      fields.push(this.pkFieldName(schemaName));
    }

    return fields;
  }

  schemaConfig(schemaName) {
    return this._mConfig.schemaConfig(schemaName);
  }

  pkFieldName(schemaName) {
    return this.schemaConfig(schemaName).utils.pk_field_name;
  }

  geometryFieldName(schemaName) {
    return this.schemaConfig(schemaName).utils.geometry_field_name;
  }

  labelFieldName(schemaName) {
    return this.schemaConfig(schemaName).utils.label_field_name;
  }

  id(schemaName, data) {
    return data[this.pkFieldName(schemaName)];
  }
}
