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

  processFormLayout(schemaName, moduleConfig) {
    const schemaConfig = this.schemaConfig(schemaName);
    const schemaLayout = schemaConfig.form.layout;
    const geometryType = this.geometryType(schemaName)
    const geometryFieldName = this.geometryFieldName(schemaName)
    return {
      type: "form",
      appearance: "fill",
      direction: "row",
      items: [
        {
          type: "map",
          key: geometryFieldName,
          edit: true,
          geometry_type: geometryType,
          gps: true,
          hidden: !geometryFieldName,
          flex: geometryFieldName ? "1" : "0",
          zoom: 12
        },
        {
          items: [
            // {
            //   "type": "message",
            //   "json": "__f__data",
            //   'flex': '0'
            // },
            // {
            //   "type": "message",
            //   "json": "__f__formGroup.value",
            //   'flex': '0'
            // },
            {
              type: "breadcrumbs",
              flex: "0",
            },
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
                `    : "Création ${schemaConfig.display.d_un_nouveau_label}";`,
                "}",
              ],
              flex: "0",
            },
            {
              flex: "0",
              type: "message",
              html: `__f__"Veuillez saisir une geometrie sur la carte"`,
              class: "error",
              hidden: `__f__${!schemaConfig.utils
                .geometry_field_name} || data.${
                schemaConfig.utils.geometry_field_name
              }?.coordinates`,
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
                  flex: "0",
                  type: "button",
                  color: "primary",
                  title: "Valider",
                  icon: "done",
                  description: "Enregistrer le contenu du formulaire",
                  action: "submit",
                  disabled: "__f__!(formGroup.valid )",
                },
                {
                  flex: "0",
                  type: "button",
                  color: "primary",
                  title: "Annuler",
                  icon: "refresh",
                  description: "Annuler l'édition",
                  action: "cancel",
                },
                {
                  // comment le mettre à gauche
                  flex: "0",
                  type: "button",
                  color: "warn",
                  title: "Supprimer",
                  icon: "delete",
                  description: "Supprimer le passage à faune",
                  action: {
                    type: "modal",
                    modal_name: "delete",
                  },

                  hidden: `__f__data.ownership > ${moduleConfig.module.cruved["D"]} || !data.${schemaConfig.utils.pk_field_name}`,
                },
                this.modalDeleteLayout(schemaConfig)
              ],
            },
          ],
        },
      ],
    };
  }

  modalDeleteLayout(schemaConfig, modalName = null) {
    return {
      type: "modal",
      modal_name: modalName || "delete",
      title: `Confirmer la suppression de l'élément`,
      direction: "row",
      items: [
        {
          type: "button",
          title: "Suppression",
          action: "delete",
          icon: "delete",
          color: "warn",
        },
        {
          type: "button",
          title: "Annuler",
          action: "close",
          icon: "refresh",
          color: "primary",
        },
      ],
    }
  }

  processPropertiesLayout(schemaConfig, moduleConfig) {
    return {
      // direction: "row",
      items: [
        // {
        //   type: "map",
        //   key: schemaConfig.utils.geometry_field_name,
        //   hidden: !schemaConfig.utils.geometry_field_name
        // },
        // {
        //   items: [
        {
          title: `__f__"Propriétés ${schemaConfig.display.du_label} " + data.${schemaConfig.utils.label_field_name}`,
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
          hidden: `__f__data.ownership > ${moduleConfig.module.cruved["U"]}`,
          flex: "0",
        },
      ],
      // },
      // ],
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

  onDelete(schemaName, data) {
    return this._mData.delete(schemaName, this.id(schemaName, data));
  }

  getFields(schemaName, layout) {
    const fields = this._mLayout.getLayoutFields(layout);

    if (
      this.geometryFieldName(schemaName) &&
      this.geometryFieldName(schemaName)
    ) {
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
    return this.schemaConfig(schemaName)?.utils.pk_field_name;
  }

  geometryFieldName(schemaName) {
    return this.schemaConfig(schemaName).utils.geometry_field_name;
  }

  geometryType(schemaName) {
    return this.geometryFieldName(schemaName)
      ? this.schemaConfig(schemaName).definition.properties[this.geometryFieldName(schemaName)].geometry_type
      : null;
  }

  labelFieldName(schemaName) {
    return this.schemaConfig(schemaName).utils.label_field_name;
  }

  id(schemaName, data) {
    return data[this.pkFieldName(schemaName)];
  }
}
