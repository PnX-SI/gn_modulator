import { Injectable, Injector } from '@angular/core';
import { ModulesDataService } from './data.service';
import { ModulesLayoutService } from './layout.service';
import { ModulesObjectService } from './object.service';
import { ModulesConfigService } from './config.service';
import { ModulesRouteService } from './route.service';
import { CommonService } from '@geonature_common/service/common.service';
import { HttpEventType, HttpResponse, HttpErrorResponse } from '@angular/common/http';
import { catchError, map, filter, switchMap } from 'rxjs/operators';
import { of } from 'rxjs';

@Injectable()
export class ModulesActionService {
  _mData: ModulesDataService;
  _mLayout: ModulesLayoutService;
  _mObject: ModulesObjectService;
  _commonService: CommonService;
  _mConfig: ModulesConfigService;
  _mRoute: ModulesRouteService;

  constructor(private _injector: Injector) {
    this._mData = this._injector.get(ModulesDataService);
    this._mLayout = this._injector.get(ModulesLayoutService);
    this._mObject = this._injector.get(ModulesObjectService);
    this._commonService = this._injector.get(CommonService);
    this._mConfig = this._injector.get(ModulesConfigService);
    this._mRoute = this._injector.get(ModulesRouteService);
  }

  processAction(event) {
    const { action, context, value = null, data = null, layout = null } = event;
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
          `Il n'y a pas d'action definie pour ${action}, ${context.object_code}`,
        );
        console.error(
          `Il n'y a pas d'action definie pour ${action}, ${context.object_code}`,
          moduleConfig.actions,
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

  processSubmit(context, data, layout) {
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
      },
    );
  }
}
