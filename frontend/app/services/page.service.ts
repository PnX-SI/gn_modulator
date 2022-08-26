import { Injectable, Injector } from "@angular/core";
import { ModulesRouteService } from "./route.service";
import { ModulesConfigService } from "./config.service";
import { ModulesRequestService } from "./request.service";
import { ModulesSchemaService } from "./schema.service";
import { CommonService } from "@geonature_common/service/common.service";


@Injectable()
export class ModulesPageService {

  _mRoute: ModulesRouteService;
  _mSchema: ModulesSchemaService;
  _mConfig: ModulesConfigService;
  _mRequest: ModulesRequestService;

  _commonService: CommonService;

  moduleCode;

  constructor(private _injector: Injector) {
    this._mRoute = this._injector.get(ModulesRouteService);
    this._mConfig = this._injector.get(ModulesConfigService);
    this._mSchema = this._injector.get(ModulesSchemaService);
    this._commonService = this._injector.get(CommonService);
    this._mRequest = this._injector.get(ModulesRequestService);
  }



  processAction({ action, objectName, schemaName=null, value=null, data=null, layout=null}) {
    if (["details", "edit", "create", "map_list"].includes(action)) {
      const moduleConfig = this._mConfig.moduleConfig(this.moduleCode);

      const pageName =
        // moduleConfig.actions[objectName] &&
        // moduleConfig.actions[objectName][action]
        // ||
        `${objectName}_${action}`;
      if (!pageName) {
        console.error(
          `Il n'y a pas d'action definie pour ${action}, ${objectName}`,
          moduleConfig.actions
        );
        return;
      }
      this._mRoute.navigateToPage(this.moduleCode, pageName, {value});
    }

    if (action == "submit") {

      this._mSchema.onSubmit(schemaName, data, layout).subscribe(
        (data) => {
          this._commonService.regularToaster(
            "success",
            `La requete a bien été effectué`
          );
          const value = this._mSchema.id(schemaName, data);
          this.processAction({
            action: "details",
            objectName,
            value
        });
        },
        (error) => {
          this._commonService.regularToaster("error", `Erreur dans la requête`);
        }
      );
    }

    if (action == "cancel") {
      if (value) {
        this.processAction({action: "details", objectName, value});
      } else {
        this.processAction({action: "map_list", objectName});
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
        filters: data.filters
      }
    );
    return url;
  }
}
