import { Component, OnInit, Injector, ViewEncapsulation } from '@angular/core';
import { ModulesLayoutComponent } from './layout.component';
import { ModulesImportService } from '../../../services/import.service';
import { HttpEventType, HttpResponse, HttpErrorResponse } from '@angular/common/http';

import utils from '../../../utils';
@Component({
  selector: 'modules-layout-import',
  templateUrl: 'layout-import.component.html',
  styleUrls: ['layout-import.component.scss', '../../base/base.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class ModulesLayoutImportComponent extends ModulesLayoutComponent implements OnInit {
  importData: {};
  importLayout: any; // layout pour l'import
  importContext: any;
  _mImport: ModulesImportService;

  uploadPercentDone;

  constructor(_injector: Injector) {
    super(_injector);
    this._name = 'layout-import';
    this.bPostComputeLayout = true;
    this._mImport = this._injector.get(ModulesImportService);
  }

  postComputeLayout() {
    this.importContext = {
      module_code: this.context.module_code,
      object_code: this.context.object_code,
    };
    this.importLayout = {
      code: 'utils.import',
    };
  }

  processImport(context, data) {
    data.importMsg = {
      html: 'Traitement en cours',
      class: null,
    };
    this._mLayout.reComputeLayout();
    this._mImport
      .importRequest(context.module_code, context.object_code, data)
      .pipe()
      .subscribe((importEvent) => {
        if (importEvent.type === HttpEventType.UploadProgress) {
          this.uploadPercentDone = Math.round((100 * importEvent.loaded) / importEvent.total);
        }
        if (importEvent instanceof HttpResponse) {
          this._mLayout.stopActionProcessing('');
          const response = importEvent.body as any;
          this.importData = response;
          // if (response.errors?.length) {
          // for (let error of response.errors) {
          // console.error(`${error.code} : ${error.msg}`);
          // }
          // data.importMsg = {
          // class: 'error',
          // html: this._mImport.importHTMLMsgError(response),
          // };
          // for (const key of response) {
          // console.log(key)
          // data[key] = response[key]
          // }
          // return;
          // }

          // let txtImport = this._mImport.importHTMLMsgSuccess(response);

          // data.importMsg = {
          //   class: 'success',
          //   html: txtImport,
          // };

          // setTimeout(() => this._mLayout.reComputeLayout(), 100);
          // this._commonService.regularToaster('success', txtImport);
        }
      });
  }

  processAction(event: any): void {
    const { action, context, value = null, data = null, layout = null } = event;
    if (action == 'import') {
      return this.processImport(context, data);
    }
  }
}
