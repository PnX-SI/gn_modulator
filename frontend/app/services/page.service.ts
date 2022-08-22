import { Injectable, Injector } from "@angular/core";
import { ModulesRouteService } from "./route.service";
import { ModulesConfigService } from "./config.service";
import { ModulesRequestService } from "./request.service";
import { ModulesSchemaService } from "./schema.service";
import { ModulesObjectService } from "./object.service";
import { CommonService } from "@geonature_common/service/common.service";


@Injectable()
export class ModulesPageService {

  _mRoute: ModulesRouteService;
  _mSchema: ModulesSchemaService;
  _mObject: ModulesObjectService
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

  processAction(action, objectName, params: any = {}) {
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
      const id = params.id;
      this._mRoute.navigateToPage(this.moduleCode, pageName, params);
    }

    if (action == "submit") {
      this._mSchema.onSubmit(objectName, params.data, params.layout).subscribe(
        (data) => {
          this._commonService.regularToaster(
            "success",
            `La requete a bien été effectué`
          );
          const id = this._mSchema.id(objectName, data);
          this.processAction("details", objectName, { value: id });
        },
        (error) => {
          this._commonService.regularToaster("error", `Erreur dans la requête`);
        }
      );
    }

    if (action == "cancel") {
      if (params.value) {
        this.processAction("details", objectName, params);
      } else {
        this.processAction("map_list", objectName, params);
      }
    }
  }

  exportUrl(moduleCode, exportCode) {
    const moduleConfig = this._mConfig.moduleConfig(moduleCode);
    const exportConfig = moduleConfig.exports.find(
      (c) => c.export_code == exportCode
    );

    const url = this._mRequest.url(
      `${this._mConfig.backendModuleUrl()}/export/${moduleCode}/${exportCode}`,
      {
        prefilters:
          this._mObject.getObjectValue(exportConfig.schema_name, "prefilters") || [],
        filters: this._mObject.getObjectValue(exportConfig.schema_name, "filters") || [],
      }
    );
    return url;
  }
}
