import { Injectable, Injector } from '@angular/core';
import { ModulesDataService } from './data.service';
import { ModulesConfigService } from './config.service';
import { ModulesSchemaService } from './schema.service';
import { Subject } from '@librairies/rxjs';

import utils from '../utils';
@Injectable()
export class ModulesObjectService {
  _mData: ModulesDataService;
  _mConfig: ModulesConfigService;
  _mSchema: ModulesSchemaService;
  _cacheObjectConfig = {};

  $reProcessObject = new Subject();

  constructor(private _injector: Injector) {
    this._mData = this._injector.get(ModulesDataService);
    this._mConfig = this._injector.get(ModulesConfigService);
    this._mSchema = this._injector.get(ModulesSchemaService);
  }

  reProcessObject(moduleCode, objectCode) {
    this.$reProcessObject.next({ moduleCode, objectCode });
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
      console.error(`L'object ${objectCode} du module ${moduleCode} n'est pas présent`);
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

    this._cacheObjectConfig[cacheKey] = utils.copy(objectConfig);

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
    const keys = [...(context.data_keys || []), key].join('.');
    return {
      ...this._mSchema.property(schemaCode, keys),
      key,
    };
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
    return this.objectConfig(context.module_code, context.object_code)?.utils.geometry_field_name;
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
    return this.objectConfigContext(context)?.schema_code;
  }

  label({ context }) {
    return this.objectConfigContext(context)?.display.label;
  }

  labels({ context }) {
    return this.objectConfigContext(context)?.display.labels;
  }

  duLabel({ context }) {
    return this.objectConfigContext(context)?.display.du_label;
  }

  desLabels({ context }) {
    return this.objectConfigContext(context)?.display.des_labels;
  }

  display({ context }) {
    return this.objectConfigContext(context).display;
  }

  dataLabel({ context, data }) {
    const label_field_name = this.objectConfigContext(context)?.utils?.label_field_name;
    return data && label_field_name && utils.getAttr(data, label_field_name);
  }

  titleDetails({ context, data }) {
    const du_label = this.objectConfigContext(context)?.display?.du_label;
    return `Détails ${du_label} ${this.dataLabel({ context, data })}`;
  }

  labelDelete({ context, data }) {
    const le_label = this.objectConfigContext(context)?.display?.le_label;
    return `Supprimer ${le_label} ${this.dataLabel({ context, data })}`;
  }

  labelEdit({ context, data }) {
    const le_label = this.objectConfigContext(context)?.display?.le_label;
    return `Modifier ${le_label} ${this.dataLabel({ context, data })}`;
  }

  labelCreate({ context }) {
    const display = this.objectConfigContext(context)?.display;
    return `Création ${display?.d_un_nouveau_label}`;
  }

  objectId({ context, data }) {
    const pkFieldName = this.objectConfigContext(context)?.utils.pk_field_name;
    return data && pkFieldName && data[pkFieldName];
  }

  titleCreateEdit({ context, data }) {
    if (!(context.module_code && context.object_code)) {
      return;
    }
    const du_label = this.objectConfigContext(context)?.display.du_label;
    const d_un_nouveau_label = this.objectConfigContext(context)?.display.d_un_nouveau_label;
    return !!this.objectId({ context, data })
      ? `Modification ${du_label} ${this.dataLabel({ context, data })}`
      : `Création ${d_un_nouveau_label}`;
  }

  tabLabel({ context }) {
    const objectConfig = this.objectConfigContext(context);
    const nbTotal = objectConfig.nb_total;
    const nbFiltered = objectConfig.nb_filtered;
    const labels = this.labels({ context });
    const objectTabLabel =
      nbFiltered == nbTotal
        ? `${utils.capitalize(labels)} (${nbTotal != null ? nbTotal : '...'})`
        : `${utils.capitalize(labels)} (${nbFiltered}/${nbTotal})`;
    return objectTabLabel;
  }

  isActionAllowed({ context, data }, action) {
    if (!(context.module_code, context.object_code)) {
      return false;
    }
    const checkAction = this.checkAction(context, action, data?.scope);
    return checkAction.actionAllowed;
  }

  urlExport({ context }, exportCode) {
    return this._mConfig.exportUrl(context.module_code, context.object_code, exportCode, {
      prefilters: context.prefilters,
      filters: context.filters,
    });
  }

  /** checkAction
   * Fonction pour vérifier
   *   so l'action peut être effectuée
   *   si le lien peut être affiché
   *
   *  input
   *    - objectCode: nom de l'objet
   *    - action: un lettre parmi 'CRUVED'
   *
   *  output
   *    - {
   *         - res: true|false
   *         - msg: message
   *      }
   *
   *    (pour les tableaux bouttons, etc....)
   * pour cela on va tester plusieurs choses :
   *
   *  - 1) le cruved est-il défini pour cet objet et pour cet action ?
   *     - l'action n'est pas affichées
   *
   *  - 2)l'utilisateur possède-t-il les droit pour faire cette action
   *      - l'action est grisé
   *      - message : vous n'avez pas les droits suffisants pour ...
   *
   *  - si oui:
   *    - action non grisée
   *    - message : modifier / voir / supprimer + txtobject
   *
   *  à appliquer dans
   *    - tableaux
   *    - boutton (detail / edit / etc...)
   */
  checkAction(context, action, scope = null) {
    // 1) cruved defini pour cet objet ?

    const objectConfig = this.objectConfigContext(context);

    const moduleConfig = this._mConfig.moduleConfig(context.module_code);

    const testObjectCruved = (objectConfig.cruved || '').includes(action);

    if ('CRU'.includes(action)) {
      const moduleConfig = this._mConfig.moduleConfig(context.module_code);

      const pageCodeAction = {
        R: 'details',
        U: 'edit',
        C: 'create',
      };
      const pageCode = `${context.object_code}_${pageCodeAction[action]}`;
      const pageExists = moduleConfig.pages && Object.keys(moduleConfig.pages).includes(pageCode);
      if (!pageExists) {
        return {
          actionAllowed: null,
          actionMsg: null,
        };
      }
    }
    if (!testObjectCruved) {
      return {
        actionAllowed: null,
        actionMsg: null,
      };
    }

    // 2) l'utilisateur à t'il le droit

    // - les droit de l'utilisateur pour ce module et pour un action (CRUVED)

    // patch pour import on teste les droits en 'C' (creation)
    const cruvedAction = action == 'I' ? 'C' : action;
    const moduleCruvedAction = moduleConfig.cruved[cruvedAction];

    // - on compare ce droit avec l'appartenance de la données
    // la possibilité d'action doit être supérieure à l'appartenance
    // - par exemple
    //    si les droit du module sont de 2 pour l'édition
    //    et que l'appartenance de la données est 3 (données autres (ni l'utilisateur ni son organisme))
    //    alors le test echoue
    // - si scope est à null => on teste seulement si l'action est bien définie sur cet object
    //   (ce qui a été testé précédemment) donc à true
    //   par exemple pour les actions d'export

    let testUserCruved;

    // si les droit du module sont nul pour cet action => FALSE
    if (!moduleCruvedAction) {
      testUserCruved = false;
      // si l'action est CREATE, EXPORT, IMPORT (ne concerne pas une ligne précise) => TRUE
    } else if ('CEI'.includes(action)) {
      testUserCruved = true;
      // pour EDIT ET READ
      // si on a pas d'info d'appartenance
      // scope null => False (par sécurité)
    } else if (scope == null) {
      testUserCruved = false;
      // on compare scope, l'appartenance qui doit être supérieur aet les droits du module
    } else {
      testUserCruved = moduleCruvedAction >= scope;
    }

    if (!testUserCruved) {
      const msgDroitsInsuffisants = {
        C: `Droits insuffisants pour créer ${objectConfig.display.un_nouveau_label}`,
        R: `Droits insuffisants pour voir ${objectConfig.display.le_label}`,
        U: `Droits insuffisants pour éditer ${objectConfig.display.le_label}`,
        V: `Droits insuffisants pour valider ${objectConfig.display.le_label}`,
        E: `Droits insuffisants pour exporter ${objectConfig.display.des_label}`,
        D: `Droits insuffisants pour supprimer ${objectConfig.display.le_label}`,
        I: `Droits insuffisants pour importer ${objectConfig.display.des_label}`,
      };
      return {
        actionAllowed: false,
        actionMsg: msgDroitsInsuffisants[action],
      };
    }

    // tests ok

    const msgTestOk = {
      C: `Créer ${objectConfig.display.un_nouveau_label}`,
      R: `Voir ${objectConfig.display.le_label}`,
      U: `Éditer ${objectConfig.display.le_label}`,
      V: `Valider ${objectConfig.display.le_label}`,
      E: `Exporter ${objectConfig.display.des_label}`,
      D: `Supprimer ${objectConfig.display.le_label}`,
      I: `Importer ${objectConfig.display.des_label}`,
    };

    return {
      actionAllowed: true,
      actionMsg: msgTestOk[action],
    };
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
      des_labels: this.desLabels.bind(this),
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
      url_export: this.urlExport.bind(this),
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
