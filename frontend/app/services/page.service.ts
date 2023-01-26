import { Injectable, Injector } from '@angular/core';
import { ModulesRouteService } from './route.service';
import { ModulesConfigService } from './config.service';
import { ModulesRequestService } from './request.service';
import { ModulesObjectService } from './object.service';
import { ModulesLayoutService } from './layout.service';
import { ModulesDataService } from './data.service';

import { CommonService } from '@geonature_common/service/common.service';
import utils from '../utils';

@Injectable()
export class ModulesPageService {
  _mRoute: ModulesRouteService;
  _mObject: ModulesObjectService;
  _mConfig: ModulesConfigService;
  _mRequest: ModulesRequestService;
  _mLayout: ModulesLayoutService;
  _mData: ModulesDataService;

  _commonService: CommonService;

  constructor(private _injector: Injector) {
    this._mRoute = this._injector.get(ModulesRouteService);
    this._mConfig = this._injector.get(ModulesConfigService);
    this._mObject = this._injector.get(ModulesObjectService);
    this._mLayout = this._injector.get(ModulesLayoutService);
    this._commonService = this._injector.get(CommonService);
    this._mRequest = this._injector.get(ModulesRequestService);
    this._mData = this._injector.get(ModulesDataService);
  }

  onSubmit(context, data, layout) {
    if (!data) {
      return;
    }

    const fields = this._mLayout.getLayoutFields(layout, context, data);

    // const processedData = utils.processData(data, layout);

    const id = this._mObject.objectId({ context, data });

    const request = id
      ? this._mData.patch(context.module_code, context.object_code, id, data, {
          fields,
        })
      : this._mData.post(context.module_code, context.object_code, data, {
          fields,
        });

    return request;
  }

  processAction({ action, context, value = null, data = null, layout = null }) {
    const moduleConfig = this._mConfig.moduleConfig(context.module_code);
    const pageConfig = moduleConfig.pages[context.page_code];
    const parentpageCode = pageConfig?.parent;
    const objectConfig = this._mObject.objectConfigContext(context);

    if (['details', 'edit', 'create', 'list'].includes(action)) {
      const moduleConfig = this._mConfig.moduleConfig(context.module_code);

      const pageCode = `${context.object_code}_${action}`;
      if (!Object.keys(moduleConfig.pages).includes(pageCode)) {
        this._commonService.regularToaster(
          'error',
          `Il n'y a pas d'action definie pour ${action}, ${context.object_code}`
        );
        console.error(
          `Il n'y a pas d'action definie pour ${action}, ${context.object_code}`,
          moduleConfig.actions
        );
        return;
      }
      const pkParams = {};
      const pkFieldName = this._mObject.pkFieldName({ context });

      if (value) {
        pkParams[pkFieldName] = value;
      }

      this._mRoute.navigateToPage(context.module_code, pageCode, {
        ...context.params,
        ...pkParams,
      });
    }

    // TODO dans la config de generic form ????
    if (action == 'submit') {
      this.onSubmit(context, data, layout).subscribe(
        (data) => {
          this._mLayout.stopActionProcessing('');
          this._commonService.regularToaster('success', `La requete a bien été effectué`);
          const value = this._mObject.objectId({ context, data });
          this.processAction({
            action: 'details',
            context,
            value,
          });
        },
        (error) => {
          this._commonService.regularToaster('error', `Erreur dans la requête`);
        }
      );
    }

    if (action == 'delete') {
      this._mObject.onDelete({ context, data }).subscribe(() => {
        this._commonService.regularToaster('success', "L'élement a bien été supprimé");
        if (objectConfig.value == this._mObject.objectId({ context, data })) {
          delete objectConfig.value;
        }

        this._mLayout.closeModals();
        this._mLayout.refreshData(context.object_code);

        if (pageConfig && pageConfig.type != 'details' && !pageConfig.root) {
          this._mRoute.navigateToPage(context.module_code, parentpageCode, data, false); // TODO params
        } else {
        }
      });
    }

    // TODO clarifier
    if (action == 'cancel') {
      if (value) {
        this.processAction({ action: 'details', context, value });
      } else {
        this._mRoute.navigateToPage(context.module_code, parentpageCode, context.params); // TODO params
      }
    }
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
  checkAction(context, action, ownership = null) {
    // 1) cruved defini pour cet objet ?
    const objectConfig = this._mObject.objectConfigContext(context);
    const moduleConfig = this._mConfig.moduleConfig(context.module_code);

    const testObjectCruved = (objectConfig.cruved || '').includes(action);

    if ('RU'.includes(action)) {
      const moduleConfig = this._mConfig.moduleConfig(context.module_code);

      const pageCodeAction = {
        R: 'details',
        U: 'edit',
      };
      const pageCode = `${context.object_code}_${pageCodeAction[action]}`;
      const pageExists = Object.keys(moduleConfig.pages).includes(pageCode);
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
    const moduleCruvedAction = moduleConfig.cruved[action];

    // - on compare ce droit avec l'appartenance de la données
    // la possibilité d'action doit être supérieure à l'appartenance
    // - par exemple
    //    si les droit du module sont de 2 pour l'édition
    //    et que l'appartenance de la données est 3 (données autres (ni l'utilisateur ni son organisme))
    //    alors le test echoue
    // - si ownership est à null => on teste seulement si l'action est bien définie sur cet object
    //   (ce qui a été testé précédemment) donc à true
    //   par exemple pour les actions d'export

    const testUserCruved = ownership ? moduleCruvedAction >= ownership : true;

    if (!testUserCruved) {
      const msgDroitsInsuffisants = {
        C: `Droits inssuffisants pour créer ${objectConfig.display.un_nouveau_label}`,
        R: `Droits inssuffisants pour voir ${objectConfig.display.le_label}`,
        U: `Droits inssuffisants pour éditer ${objectConfig.display.le_label}`,
        V: `Droits inssuffisants pour valider ${objectConfig.display.le_label}`,
        E: `Droits inssuffisants pour exporter ${objectConfig.display.des_label}`,
        D: `Droits inssuffisants pour supprimer ${objectConfig.display.le_label}`,
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
    };

    return {
      actionAllowed: true,
      actionMsg: msgTestOk[action],
    };
  }
}
