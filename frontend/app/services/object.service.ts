import { Injectable, Injector } from '@angular/core';
import { ModulesDataService } from './data.service';
import { ModulesConfigService } from './config.service';
import { ModulesSchemaService } from './schema.service';
import utils from '../utils';
@Injectable()
export class ModulesObjectService {
  _mData: ModulesDataService;
  _mConfig: ModulesConfigService;
  _mSchema: ModulesSchemaService;
  _cacheObjectConfig = {};

  constructor(private _injector: Injector) {
    this._mData = this._injector.get(ModulesDataService);
    this._mConfig = this._injector.get(ModulesConfigService);
    this._mSchema = this._injector.get(ModulesSchemaService);
  }

  /** renvoie la configuration d'un object en fonction de
   * - moduleCode
   * - objectCode
   * - pageCode
   * - params
   */
  objectConfig(moduleCode, objectCode, pageCode = null, params: any = null) {
    // config provenant du module

    const cacheKey = this.objectConfigCacheKey(moduleCode, objectCode, pageCode, params);

    if (this._cacheObjectConfig[cacheKey]) {
      return this._cacheObjectConfig[cacheKey];
    }

    if (!(moduleCode && objectCode)) {
      return;
    }

    const moduleConfig = this._mConfig.moduleConfig(moduleCode);

    if (!moduleConfig) {
      return;
    }

    const objectModuleConfig = this._mConfig.moduleConfig(moduleCode).objects[objectCode];
    if (!objectModuleConfig) {
      // console.error(`L'object ${objectCode} du module ${moduleCode} n'est pas présent`);
      return;
    }

    if (!(pageCode || params)) {
      this._cacheObjectConfig[cacheKey] = objectModuleConfig;
      return objectModuleConfig;
    }

    // config provenant de la page
    let objectPageConfig: any = {};
    if (pageCode) {
      const pageConfig: any = this._mConfig.pageConfig(moduleCode, pageCode);

      objectPageConfig = (pageConfig?.objects && pageConfig.objects[objectCode]) || {};
    }

    let objectConfig = {
      ...(objectModuleConfig || {}),
      ...objectPageConfig,
    };

    if (!params) {
      this._cacheObjectConfig[cacheKey] = objectConfig;
      return objectConfig;
    }

    // à mettre ailleurs (ou à résoudre au dernier moment ?)
    for (const [paramKey, paramValue] of Object.entries(params)) {
      objectConfig = utils.replace(objectConfig, `:${paramKey}`, paramValue);
    }

    this._cacheObjectConfig[cacheKey] = objectConfig;
    return objectConfig;
  }

  objectConfigCacheKey(moduleCode, objectCode, pageCode, params) {
    return `${moduleCode}__${objectCode}__${pageCode}__${JSON.stringify(params)}`;
  }

  objectConfigContext(context) {
    return this.objectConfig(
      context.module_code,
      context.object_code,
      context.page_code,
      context.params
    );
  }

  objectConfigLayout({ context }, object_code = null) {
    return this.objectConfig(
      context.module_code,
      object_code || context.object_code,
      context.page_code,
      context.params
    );
  }

  property(context, key) {
    const schemaCode = this.objectConfigContext(context).schema_code;
    return this._mSchema.property(schemaCode, key);
  }

  setObjectConfig(context, config) {
    let objectConfig = this.objectConfigContext(context);
    for (const key of Object.keys(config)) {
      objectConfig[key] = config[key];
    }
  }

  pkFieldName({ context }) {
    return this.objectConfig(context.module_code, context.object_code)?.utils.pk_field_name;
  }

  geometryFieldName({ context }) {
    return this.objectConfig(context.module_code, context.object_code).utils.geometry_field_name;
  }

  geometryType({ context }) {
    return this.geometryFieldName({ context })
      ? this.objectConfig(context.module_code, context.object_code).properties[
          this.geometryFieldName({ context })
        ].geometry_type
      : null;
  }

  labelFieldName({ context }) {
    return this.objectConfig(context.module_code, context.object_code).utils.label_field_name;
  }

  preFilters({ context }) {
    return context.prefilters;
  }

  filters({ context }) {
    return context.filters;
  }

  value({ context }) {
    return context.value;
  }

  schemaCode({ context }) {
    return this.objectConfigContext(context).schema_code;
  }

  label({ context }) {
    return this.objectConfigContext(context).display.label;
  }

  labels({ context }) {
    return this.objectConfigContext(context).display.labels;
  }

  duLabel({ context }) {
    return this.objectConfigContext(context).display.du_label;
  }

  display({ context }) {
    return this.objectConfigContext(context).display;
  }

  dataLabel({ context, data }) {
    const label_field_name = this.objectConfigContext(context).utils?.label_field_name;
    return data && label_field_name && data[label_field_name];
  }

  titleDetails({ context, data }) {
    const du_label = this.objectConfigContext(context).display?.du_label;
    return `Détails ${du_label} ${this.dataLabel({ context, data })}`;
  }

  labelDelete({ context, data }) {
    const le_label = this.objectConfigContext(context).display?.le_label;
    return `Supprimer ${le_label} ${this.dataLabel({ context, data })}`;
  }

  labelEdit({ context, data }) {
    const le_label = this.objectConfigContext(context).display?.le_label;
    return `Modifier ${le_label} ${this.dataLabel({ context, data })}`;
  }

  labelCreate({ context }) {
    const display = this.objectConfigContext(context).display;
    return `Création ${display?.d_un_nouveau_label}`;
  }

  objectId({ context, data }) {
    const pkFieldName = this.objectConfigContext(context).utils.pk_field_name;
    return data && pkFieldName && data[pkFieldName];
  }

  titleCreateEdit({ context, data }) {
    if (!(context.module_code && context.object_code)) {
      return;
    }
    const du_label = this.objectConfigContext(context).display.du_label;
    const d_un_nouveau_label = this.objectConfigContext(context).display.d_un_nouveau_label;
    return !!this.objectId({ context, data })
      ? `Modification ${du_label} ${this.dataLabel({ context, data })}`
      : `Création ${d_un_nouveau_label}`;
  }

  tabLabel({ context }) {
    const objectConfig = this.objectConfigContext(context);
    const nbTotal = objectConfig.nb_total;
    const nbFiltered = objectConfig.nb_filtered;
    const labels = this.labels({ context });
    const objectTabLabel = nbTotal
      ? `${utils.capitalize(labels)} (${nbFiltered}/${nbTotal})`
      : `${utils.capitalize(labels)} (0)`;
    return objectTabLabel;
  }

  isActionAllowed({ context, data }, action) {
    const moduleCruvedAction = this._mConfig.moduleConfig(context.module_code).cruved[action];
    const ownership = data && data.ownership;
    if (!ownership) {
      return true;
    }
    return moduleCruvedAction >= ownership;
  }

  utilsObject() {
    return {
      value: this.value.bind(this),
      prefilters: this.preFilters.bind(this),
      filters: this.filters.bind(this),
      config: this.objectConfigContext.bind(this),
      schema_code: this.schemaCode.bind(this),
      label: this.label.bind(this),
      du_label: this.duLabel.bind(this),
      data_label: this.dataLabel.bind(this),
      labels: this.labels.bind(this),
      tab_label: this.tabLabel.bind(this),
      title_details: this.titleDetails.bind(this),
      title_create_edit: this.titleCreateEdit.bind(this),
      label_delete: this.labelDelete.bind(this),
      label_edit: this.labelEdit.bind(this),
      label_create: this.labelCreate.bind(this),
      is_action_allowed: this.isActionAllowed.bind(this),
      geometry_field_name: this.geometryFieldName.bind(this),
      geometry_type: this.geometryType.bind(this),
      object: this.objectConfigLayout.bind(this),
    };
  }

  onDelete({ context, data }) {
    return this._mData.delete(
      context.module_code,
      context.object_code,
      this.objectId({ context, data })
    );
  }
}
