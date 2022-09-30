import { Injectable, Injector } from "@angular/core";
import { ModulesRouteService } from "./route.service";
import { ModulesConfigService } from "./config.service";
import { ModulesRequestService } from "./request.service";
import { ModulesSchemaService } from "./schema.service";
import { ModulesLayoutService } from "./layout.service";
import { CommonService } from "@geonature_common/service/common.service";
import { of } from "@librairies/rxjs";
import { mergeMap } from "@librairies/rxjs/operators";

@Injectable()
export class ModulesPageService {
  _mRoute: ModulesRouteService;
  _mSchema: ModulesSchemaService;
  _mConfig: ModulesConfigService;
  _mRequest: ModulesRequestService;
  _mLayout: ModulesLayoutService;

  _commonService: CommonService;

  moduleCode;
  breadcrumbs = [];
  pageName;
  // pageParams;
  // pageQueryParams;
  // pageAllParams;
  params;

  constructor(private _injector: Injector) {
    this._mRoute = this._injector.get(ModulesRouteService);
    this._mConfig = this._injector.get(ModulesConfigService);
    this._mSchema = this._injector.get(ModulesSchemaService);
    this._mLayout = this._injector.get(ModulesLayoutService);
    this._commonService = this._injector.get(CommonService);
    this._mRequest = this._injector.get(ModulesRequestService);
  }

  setCurrentPage(pageName) {
    this.pageName = pageName;
  }

  processAction({
    action,
    objectName,
    schemaName = null,
    value = null,
    data = null,
    layout = null
  }) {

    const moduleConfig = this._mConfig.moduleConfig(this.moduleCode);
    const pageConfig = moduleConfig.pages[this.pageName];
    const parentPageName = pageConfig.parent;


    if (["details", "edit", "create", "list"].includes(action)) {
      const moduleConfig = this._mConfig.moduleConfig(this.moduleCode);

      const pageName = `${objectName}_${action}`;
      if (!pageName) {
        this._commonService.regularToaster(
          "error",
          `Il n'y a pas d'action definie pour ${action}, ${objectName}`
        );
        console.error(
          `Il n'y a pas d'action definie pour ${action}, ${objectName}`,
          moduleConfig.actions
        );
        return;
      }
      // const routeParams = { value, ...((layout as any)?.params || {}) };
      const routeParams = {};
      // routeParams[]
      const schemaName = moduleConfig.data[objectName].schema_name;

      routeParams[this._mSchema.pkFieldName(schemaName)] = value;
      // this._mRoute.navigateToPage(this.moduleCode, pageName, routeParams);
      this._mRoute.navigateToPage(this.moduleCode, pageName, {...this.params, ...routeParams });
    }

    // TODO dans la config de generic form ????
    if (action == "submit") {
      this._mSchema.onSubmit(schemaName, data, layout).subscribe(
        (data) => {
          this._mLayout.stopActionProcessing('');
          this._commonService.regularToaster(
            "success",
            `La requete a bien été effectué`
          );
          const value = this._mSchema.id(schemaName, data);
          this.processAction({
            action: "details",
            objectName,
            value,
          });
        },
        (error) => {
          this._commonService.regularToaster("error", `Erreur dans la requête`);
        }
      );
    }

    if(action == "delete") {
      this._mSchema.onDelete(schemaName, data).subscribe(() => {
        this._commonService.regularToaster('success', "L'élement a bien été supprimé");
        this._mLayout.closeModals()
        this._mLayout.refreshData(objectName);

        if(pageConfig.type != 'details' && !pageConfig.root) {
          this._mRoute.navigateToPage(this.moduleCode, parentPageName, data); // TODO params
        } else {
        }
      })
    }

    // TODO clarifier
    if (action == "cancel") {
      if (value) {
        this.processAction({ action: "details", objectName, value });
      } else {
        this._mRoute.navigateToPage(this.moduleCode, parentPageName, this.params); // TODO params
      }
    }
  }

  exportUrl(moduleCode, exportCode, data) {
    const moduleConfig = this._mConfig.moduleConfig(moduleCode);
    const exportConfig = moduleConfig.exports.find(
      (c) => c.export_code == exportCode
    );

    const url = this._mRequest.url(
      `${this._mConfig.backendModuleUrl()}/export/${moduleCode}/${exportCode}`,
      {
        prefilters: data.prefilters,
        filters: data.filters,
      }
    );
    return url;
  }

  getBreadcrumbs() {
    return this._mRequest.request('get',  `${this._mConfig.backendModuleUrl()}/breadcrumbs/${this.moduleCode}/${this.pageName}`, { params: this.params} )
    .pipe(
      mergeMap((breadcrumbs)=> {
        this.breadcrumbs = breadcrumbs;
        return of(true)
      })
    );
  }
}
