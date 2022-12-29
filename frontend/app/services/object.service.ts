import { Injectable, Injector } from '@angular/core';
import { ModulesDataService } from './data.service';
import { ModulesConfigService } from './config.service';
import utils from '../utils';
@Injectable()
export class ModulesObjectService {
  _mData: ModulesDataService;
  _mConfig: ModulesConfigService;

  _cacheObjectConfig = {};

  constructor(private _injector: Injector) {
    this._mData = this._injector.get(ModulesDataService);
    this._mConfig = this._injector.get(ModulesConfigService);
  }

  /** renvoie la configuration d'un object en fonction de
   * - moduleCode
   * - objectCode
   * - pageCode
   * - params
   */
  objectConfig(moduleCode, objectCode, pageCode = null, params: any = null) {
    // config provenant du module

    if (!(moduleCode && objectCode)) {
      return {};
    }

    const moduleConfig = this._mConfig.moduleConfig(moduleCode);

    if (!moduleConfig) {
      return {};
    }

    const objectModuleConfig = this._mConfig.moduleConfig(moduleCode).objects[objectCode];
    if (!objectModuleConfig) {
      // console.error(`L'object ${objectCode} du module ${moduleCode} n'est pas présent`);
      return {};
    }

    if (!(pageCode || params)) {
      return objectModuleConfig;
    }

    // config provenant de la page
    let objectPageConfig: any = {};
    if (pageCode) {
      const pageConfig: any = this._mConfig.pageConfig(moduleCode, pageCode);
      objectPageConfig = pageConfig.objects[objectCode] || {};
    }

    let objectConfig = {
      ...objectModuleConfig,
      ...objectPageConfig,
    };

    if (!params) {
      return objectConfig;
    }

    // à mettre ailleurs (ou à résoudre au dernier moment ?)
    for (const [paramKey, paramValue] of Object.entries(params)) {
      objectConfig = utils.replace(objectConfig, `:${paramKey}`, paramValue);
    }

    return objectConfig;
  }

  objectConfigCacheKey(moduleCode, objectCode, pageCode, params) {
    return `${moduleCode}__${objectCode}__${pageCode}__${JSON.stringify(params)}`;
  }

  objectConfigContext(context) {
    const cacheKey = this.objectConfigCacheKey(
      context.module_code,
      context.object_code,
      context.page_code,
      context.params
    );
    if (!this._cacheObjectConfig[cacheKey]) {
      this._cacheObjectConfig[cacheKey] = utils.copy(
        this.objectConfig(
          context.module_code,
          context.object_code,
          context.page_code,
          context.params
        )
      );
    }
    return this._cacheObjectConfig[cacheKey];
  }

  property(context, key) {
    const objectConfig = this.objectConfigContext(context);
    return {
      key,
      ...objectConfig.properties[key]
    };
  }

  setObjectConfig(context, config) {
    let objectConfig = this.objectConfigContext(context);
    for (const key of Object.keys(config)) {
      objectConfig[key] = config[key];
    }
  }

  pkFieldName(moduleCode, objectCode) {
    return this.objectConfig(moduleCode, objectCode)?.utils.pk_field_name;
  }

  geometryFieldName(moduleCode, objectCode) {
    return this.objectConfig(moduleCode, objectCode).utils.geometry_field_name;
  }

  geometryType(moduleCode, objectCode) {
    return this.geometryFieldName(moduleCode, objectCode)
      ? this.objectConfig(moduleCode, objectCode).properties[
          this.geometryFieldName(moduleCode, objectCode)
        ].geometry_type
      : null;
  }

  labelFieldName(moduleCode, objectCode) {
    return this.objectConfig(moduleCode, objectCode).utils.label_field_name;
  }

  objectId(moduleCode, objectCode, data) {
    return data[this.pkFieldName(moduleCode, objectCode)];
  }

  objectPreFilters({ context }) {
    return context.prefilters;
  }

  objectFilters({ context }) {
    return context.filters;
  }

  objectValue({ context }) {
    return context.value;
  }

  objectSchemaCode({ context }) {
    return this.objectConfigContext(context).schema_code;
  }

  objectLabel({ context }) {
    return this.objectConfigContext(context).display.label;
  }

  objectLabels({ context }) {
    return this.objectConfigContext(context).display.labels;
  }

  objectDuLabel({ context }) {
    return this.objectConfigContext(context).display.du_label;
  }

  objectTitleDetails({ context, data }) {
    const du_label = this.objectConfigContext(context).display.du_label;
    const label_field_name = this.objectConfigContext(context).utils.label_field_name;
    return `Détails ${du_label} ${data[label_field_name]}`;
  }

  objectTitleCreateEdit({ context, data }) {
    const du_label = this.objectConfigContext(context).display.du_label;
    const du_nouveau_label = this.objectConfigContext(context).display.du_nouveau_label;
    const labelFieldName = this.objectConfigContext(context).utils.label_field_name;
    const pkFieldName = this.objectConfigContext(context).utils.pk_field_name;
    const id = data[pkFieldName];
    return !!id
      ? `Modification ${du_label} ${data[labelFieldName]}`
      : `Création ${du_nouveau_label}`;
  }

  objectTabLabel({ data, context }) {
    const nbTotal = data.nb_total;
    const nbFiltered = data.nb_filtered;
    const labels = this.objectLabel({ context });
    return nbTotal
      ? `${utils.capitalize(labels)} (${nbFiltered}/${nbTotal})`
      : `${utils.capitalize(labels)}`;
  }

  processFormLayout(moduleCode, objectCode) {
    const objectConfig = this.objectConfig(moduleCode, objectCode);
    const moduleConfig = this._mConfig.moduleConfig(moduleCode);
    const schemaLayout = objectConfig.form.layout;
    const geometryType = this.geometryType(moduleCode, objectCode);
    const geometryFieldName = this.geometryFieldName(moduleCode, objectCode);
    return {
      type: 'form',
      appearance: 'fill',
      direction: 'row',
      items: [
        {
          type: 'map',
          key: geometryFieldName,
          edit: true,
          geometry_type: geometryType,
          gps: true,
          hidden: !geometryFieldName,
          flex: geometryFieldName ? '1' : '0',
          zoom: 12,
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
              type: 'breadcrumbs',
              flex: '0',
            },
            {
              title: [
                '__f__{',
                `  const id = data.${objectConfig.utils.pk_field_name};`,
                '  return id',
                '    ? `Modification ' +
                  objectConfig.display.du_label +
                  ' ${data.' +
                  objectConfig.utils.label_field_name +
                  '}`',
                `    : "Création ${objectConfig.display.d_un_nouveau_label}";`,
                '}',
              ],
              flex: '0',
            },
            {
              flex: '0',
              type: 'message',
              html: `__f__"Veuillez saisir une geometrie sur la carte"`,
              class: 'error',
              hidden: `__f__${!objectConfig.utils.geometry_field_name} || data.${
                objectConfig.utils.geometry_field_name
              }?.coordinates`,
            },
            {
              items: schemaLayout,
              overflow: true,
            },
            {
              flex: '0',
              direction: 'row',
              items: [
                {
                  flex: '0',
                  type: 'button',
                  color: 'primary',
                  title: 'Valider',
                  icon: 'done',
                  description: 'Enregistrer le contenu du formulaire',
                  action: 'submit',
                  disabled: '__f__!(formGroup.valid )',
                },
                {
                  flex: '0',
                  type: 'button',
                  color: 'primary',
                  title: 'Annuler',
                  icon: 'refresh',
                  description: "Annuler l'édition",
                  action: 'cancel',
                },
                {
                  // comment le mettre à gauche
                  flex: '0',
                  type: 'button',
                  color: 'warn',
                  title: 'Supprimer',
                  icon: 'delete',
                  description: 'Supprimer le passage à faune',
                  action: {
                    type: 'modal',
                    modal_name: 'delete',
                  },

                  hidden: `__f__data.ownership > ${moduleConfig.cruved['D']} || !data.${objectConfig.utils.pk_field_name}`,
                },
                this.modalDeleteLayout(objectConfig),
              ],
            },
          ],
        },
      ],
    };
  }

  modalDeleteLayout(objectConfig, modalName: any = null) {
    return {
      type: 'modal',
      modal_name: modalName || 'delete',
      title: `Confirmer la suppression de l'élément`,
      direction: 'row',
      items: [
        {
          type: 'button',
          title: 'Suppression',
          action: 'delete',
          icon: 'delete',
          color: 'warn',
        },
        {
          type: 'button',
          title: 'Annuler',
          action: 'close',
          icon: 'refresh',
          color: 'primary',
        },
      ],
    };
  }

  processPropertiesLayout(moduleCode, objectCode) {
    const objectConfig = this.objectConfig(moduleCode, objectCode);
    const moduleConfig = this._mConfig.moduleConfig(moduleCode);
    return {
      // direction: "row",
      items: [
        // {
        //   type: "map",
        //   key: objectConfig.utils.geometry_field_name,
        //   hidden: !objectConfig.utils.geometry_field_name
        // },
        // {
        //   items: [
        {
          title: `__f__"Propriétés ${objectConfig.display.du_label} " + data.${objectConfig.utils.label_field_name}`,
          flex: '0',
        },
        {
          items: objectConfig.details.layout,
          overflow: true,
        },
        {
          type: 'button',
          color: 'primary',
          title: 'Éditer',
          description: `Editer ${objectConfig.display.le_label}`,
          action: 'edit',
          hidden: `__f__data.ownership > ${moduleConfig.cruved['U']}`,
          flex: '0',
        },
      ],
      // },
      // ],
    };
  }

  onSubmit(moduleCode, objectCode, data, layout) {
    if (!data) {
      return;
    }

    const fields = this.getFields(moduleCode, objectCode, layout);

    const processedData = utils.processData(data, layout);

    const id = this.objectId(moduleCode, objectCode, data);

    const request = id
      ? this._mData.patch(moduleCode, objectCode, id, processedData, {
          fields,
        })
      : this._mData.post(moduleCode, objectCode, processedData, {
          fields,
        });

    return request;
  }

  onDelete(moduleCode, objectCode, data) {
    return this._mData.delete(moduleCode, objectCode, this.objectId(moduleCode, objectCode, data));
  }

  getFields(moduleCode, objectCode, layout) {
    const fields = utils.getLayoutFields(layout);

    if (
      this.geometryFieldName(moduleCode, objectCode) &&
      this.geometryFieldName(moduleCode, objectCode)
    ) {
      fields.push(this.geometryFieldName(moduleCode, objectCode));
    }

    if (!fields.includes(this.pkFieldName(moduleCode, objectCode))) {
      fields.push(this.pkFieldName(moduleCode, objectCode));
    }

    if (!fields.includes(this.labelFieldName(moduleCode, objectCode))) {
      fields.push(this.labelFieldName(moduleCode, objectCode));
    }


    return fields;
  }
}
