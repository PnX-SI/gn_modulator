import { Injectable, Injector } from '@angular/core';
import { ModulesRouteService } from './route.service';
import { ModulesConfigService } from './config.service';
import { ModulesRequestService } from './request.service';
import { ModulesObjectService } from './object.service';
import { ModulesLayoutService } from './layout.service';
import { CommonService } from '@geonature_common/service/common.service';
import { of } from '@librairies/rxjs';
import { mergeMap } from '@librairies/rxjs/operators';

@Injectable()
export class ModulesPageService {
  _mRoute: ModulesRouteService;
  _mObject: ModulesObjectService;
  _mConfig: ModulesConfigService;
  _mRequest: ModulesRequestService;
  _mLayout: ModulesLayoutService;

  _commonService: CommonService;

  breadcrumbs = [];
  moduleCode;
  moduleConfig;
  pageCode;
  pageConfig;
  params;

  constructor(private _injector: Injector) {
    this._mRoute = this._injector.get(ModulesRouteService);
    this._mConfig = this._injector.get(ModulesConfigService);
    this._mObject = this._injector.get(ModulesObjectService);
    this._mLayout = this._injector.get(ModulesLayoutService);
    this._commonService = this._injector.get(CommonService);
    this._mRequest = this._injector.get(ModulesRequestService);
  }

  setCurrentPage(pageCode, pageConfig) {
    this.pageCode = pageCode;
    this.pageConfig = pageConfig;
  }

  processAction({ action, objectCode, value = null, data = null, layout = null }) {
    const moduleConfig = this._mConfig.moduleConfig(this.moduleCode);
    const pageConfig = moduleConfig.pages[this.pageCode];
    const parentpageCode = pageConfig.parent;

    if (['details', 'edit', 'create', 'list'].includes(action)) {
      const moduleConfig = this._mConfig.moduleConfig(this.moduleCode);

      const pageCode = `${objectCode}_${action}`;
      if (!pageCode) {
        this._commonService.regularToaster(
          'error',
          `Il n'y a pas d'action definie pour ${action}, ${objectCode}`
        );
        console.error(
          `Il n'y a pas d'action definie pour ${action}, ${objectCode}`,
          moduleConfig.actions
        );
        return;
      }
      // const routeParams = { value, ...((layout as any)?.params || {}) };
      const routeParams = {};
      // routeParams[]
      const schemaName = moduleConfig.objects[objectCode].schema_code;

      routeParams[this._mConfig.pkFieldName(this.moduleCode, objectCode)] = value;
      // this._mRoute.navigateToPage(this.moduleCode, pageCode, routeParams);
      this._mRoute.navigateToPage(this.moduleCode, pageCode, { ...this.params, ...routeParams });
    }

    // TODO dans la config de generic form ????
    if (action == 'submit') {
      this._mObject.onSubmit(this.moduleCode, objectCode, data, layout).subscribe(
        (data) => {
          this._mLayout.stopActionProcessing('');
          this._commonService.regularToaster('success', `La requete a bien été effectué`);
          const value = this._mConfig.objectId(this.moduleCode, objectCode, data);
          this.processAction({
            action: 'details',
            objectCode,
            value,
          });
        },
        (error) => {
          this._commonService.regularToaster('error', `Erreur dans la requête`);
        }
      );
    }

    if (action == 'delete') {
      this._mObject.onDelete(this.moduleCode, objectCode, data).subscribe(() => {
        this._commonService.regularToaster('success', "L'élement a bien été supprimé");
        this._mLayout.closeModals();
        this._mLayout.refreshData(objectCode);

        if (pageConfig.type != 'details' && !pageConfig.root) {
          this._mRoute.navigateToPage(this.moduleCode, parentpageCode, data); // TODO params
        } else {
        }
      });
    }

    // TODO clarifier
    if (action == 'cancel') {
      if (value) {
        this.processAction({ action: 'details', objectCode, value });
      } else {
        this._mRoute.navigateToPage(this.moduleCode, parentpageCode, this.params); // TODO params
      }
    }
  }

  reset() {
    this.breadcrumbs = [];
    this.moduleCode = null;
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
  checkAction(moduleCode, objectCode, action, ownership = null) {
    // 1) cruved defini pour cet objet ?
    const objectConfig = this._mConfig.objectConfig(moduleCode, objectCode);
    const testObjectCruved = (objectConfig.cruved || '').includes(action);

    if (!testObjectCruved) {
      return {
        actionAllowed: null,
        actionMsg: null,
      };
    }

    // 2) l'utilisateur à t'il le droit

    // - les droit de l'utilisateur pour ce module et pour un action (CRUVED)
    const cruvedAction = this.moduleConfig.cruved[action];

    // - on compare ce droit avec l'appartenance de la données
    // la possibilité d'action doit être supérieure à l'appartenance
    // - par exemple
    //    si les droit du module sont de 2 pour l'édition
    //    et que l'appartenance de la données est 3 (données autres (ni l'utilisateur ni son organisme))
    //    alors le test echoue
    // - si ownership est à null => on teste seulement si l'action est bien définie sur cet object
    //   (ce qui a été testé précédemment) donc à true
    //   par exemple pour les actions d'export

    const testUserCruved = ownership ? cruvedAction >= ownership : true;

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
