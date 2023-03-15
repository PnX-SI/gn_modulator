import { Injectable, Injector } from '@angular/core';
import { ModulesDataService } from './data.service';
import { ModulesLayoutService } from './layout.service';
import { ModulesObjectService } from './object.service';
import { ModulesConfigService } from './config.service';
import { ModulesRouteService } from './route.service';
import { ModulesRequestService } from './request.service';
import { CommonService } from '@geonature_common/service/common.service';
import { HttpEventType, HttpResponse, HttpErrorResponse } from '@angular/common/http';
import { catchError, map, filter, switchMap } from 'rxjs/operators';
import { of } from 'rxjs';

@Injectable()
export class ModulesImportService {
  _mData: ModulesDataService;
  _mLayout: ModulesLayoutService;
  _mObject: ModulesObjectService;
  _commonService: CommonService;
  _mConfig: ModulesConfigService;
  _mRoute: ModulesRouteService;
  _mRequest: ModulesRequestService;

  constructor(private _injector: Injector) {
    this._mData = this._injector.get(ModulesDataService);
    this._mLayout = this._injector.get(ModulesLayoutService);
    this._mObject = this._injector.get(ModulesObjectService);
    this._commonService = this._injector.get(CommonService);
    this._mConfig = this._injector.get(ModulesConfigService);
    this._mRoute = this._injector.get(ModulesRouteService);
    this._mRequest = this._injector.get(ModulesRequestService);
  }

  importRequest(moduleCode, object_code, data, params = {}) {
    return this._mRequest.postRequestWithFormData(
      `${this._mConfig.backendModuleUrl()}/import/${moduleCode}/${object_code}/${
        data.id_import || ''
      }`,
      {
        data,
        params,
      }
    );
  }

  processImport(context, data) {
    data.importMsg = {
      html: 'Traitement en cours',
      class: null,
    };
    this._mLayout.reComputeLayout();
    this.importRequest(context.module_code, context.object_code, data)
      .pipe()
      .subscribe(
        (importEvent) => {
          if (importEvent.type === HttpEventType.UploadProgress) {
            const uploadPerCentDone = Math.round((100 * importEvent.loaded) / importEvent.total);
          }
          if (importEvent instanceof HttpResponse) {
            this._mLayout.stopActionProcessing('');
            const response = importEvent.body as any;
            if (response.errors?.length) {
              for (let error of response.errors) {
                console.error(`${error.code} : ${error.msg}`);
              }
              data.importMsg = {
                class: 'error',
                html: this.importHTMLMsgError(response),
              };
              return;
            }

            let txtImport = this.importHTMLMsgSuccess(response);

            data.importMsg = {
              class: 'success',
              html: txtImport,
            };

            setTimeout(() => this._mLayout.reComputeLayout(), 100);
            // this._commonService.regularToaster('success', txtImport);
          }
        },
        (error: HttpErrorResponse) => {
          this._commonService.regularToaster('error', `Import : ${error.error.msg}`);
        }
      );
  }

  importHTMLMsgSuccess(impt) {
    let txtImport = `<h5>Import réussi</h5>`;
    let res = impt.res;

    if (res.nb_data) {
      txtImport += `data: ${res.nb_data}<br>`;
    }

    if (res.nb_raw != res.nb_data) {
      txtImport += `raw: ${res.nb_raw}<br>`;
    }

    if (res.nb_insert) {
      txtImport += `insert: ${res.nb_insert}<br>`;
    }

    if (res.nb_update) {
      txtImport += `update: ${res.nb_update}<br>`;
    }

    if (res.nb_unchanged) {
      txtImport += `unchanged: ${res.nb_unchanged}<br>`;
    }
    return txtImport;
  }

  importHTMLMsgError(impt) {
    let txtImport = `<h4>${impt.errors.length} erreurs</h4>`;

    let txtErrorRequired;
    for (let error of impt.errors.filter((e) => e.code == 'ERR_IMPORT_REQUIRED')) {
      if (!txtErrorRequired) {
        txtErrorRequired = `<h5>Champs requis manquants</h5>`;
      }
      txtErrorRequired += `<b>${error.key}</b> ${error.lines.length} ligne(s): [${error.lines}]<br>`;
    }
    if (txtErrorRequired) {
      txtImport += '<hr>';
      txtImport += txtErrorRequired;
    }

    let txtErrorUnresolved;
    for (let error of impt.errors.filter((e) => e.code == 'ERR_IMPORT_UNRESOLVED')) {
      if (!txtErrorUnresolved) {
        txtErrorUnresolved = `<h5>Champs non résolus</h5>`;
      }
      txtErrorUnresolved += `<b>${error.key}</b> ${error.lines.length} ligne(s): [${error.lines}]<br>`;
      if (error.values) {
        txtErrorUnresolved += `Valeurs parmi : ${error.values
          .map((v) => v.cd_nomenclature)
          .join(', ')}<br>`;
      }
    }
    if (txtErrorUnresolved) {
      txtImport += '<hr>';
      txtImport += txtErrorUnresolved;
    }

    for (let error of impt.errors.filter(
      (e) => !['ERR_IMPORT_REQUIRED', 'ERR_IMPORT_UNRESOLVED'].includes(e.code)
    )) {
      txtImport += '<hr>';
      txtImport += `${error.code}: ${error.msg}`;
    }

    return txtImport;
  }
}
