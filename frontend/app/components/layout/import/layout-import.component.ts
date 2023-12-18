import { Component, OnInit, Injector, ViewEncapsulation, ViewChild } from '@angular/core';
import { ModulesLayoutComponent } from '../base/layout.component';
import { ModulesImportService } from '../../../services/import.service';
import { ModulesDataService } from '../../../services/data.service';
import { HttpEventType, HttpResponse, HttpErrorResponse } from '@angular/common/http';
import { MatStepper } from '@angular/material/stepper';

import utils from '../../../utils';
@Component({
  selector: 'modules-layout-import',
  templateUrl: 'layout-import.component.html',
  styleUrls: ['layout-import.component.scss', '../../base/base.scss'],
})
export class ModulesLayoutImportComponent extends ModulesLayoutComponent implements OnInit {
  importData: any = {};
  importLayout: any; // layout pour l'import
  importContext: any;
  _mImport: ModulesImportService;
  _mData: ModulesDataService;

  step = 0;

  uploadPercentDone;

  editableStep = false;

  importMsg: any = {};

  importDataTest = {
    status: 'DONE',
    res: {
      nb_data: 367,
      nb_insert: 0,
      nb_process: 367,
      nb_raw: 367,
      nb_unchanged: 367,
      nb_update: 0,
    },
    id_import: 1,
    options: {},
  };

  // @ViewChild('stepper') stepper: MatStepper;

  constructor(_injector: Injector) {
    super(_injector);
    this._name = 'layout-import';
    this.bPostComputeLayout = true;
    this._mImport = this._injector.get(ModulesImportService);
    this._mData = this._injector.get(ModulesDataService);
  }

  postProcessLayout() {
    this.initImport();
  }

  initImport() {
    this.importContext = {
      module_code: this.context.module_code,
      object_code: this.context.object_code,
    };
    this.importLayout = {
      code: 'utils.import',
    };
    // this._mLayout.getFormControl('form_import')?.reset()
    this.importData = this.computedLayout.test_import ? utils.copy(this.importDataTest) : {};
    this.setStep();
  }

  setStep() {
    this.importData.importMsg = this._mImport.processMessage(this.importData);
    this.importData.errorMsgType = this._mImport.processErrorsType(this.importData);
    this.importData.errorMsgLine = this._mImport.processErrorsLine(this.importData);
  }

  apiFields = ['res', 'status', 'id_import', 'errors'];

  processImport(context, data) {
    // gestion des options
    if (data.options.check_first) {
      data.options['target_step'] = 'count';
    }

    this._subs['process_import'] = this._mImport
      .importRequest(
        context.module_code,
        context.object_code,
        data,
        { fields: this.apiFields },
        !!this.computedLayout.admin,
      )
      .pipe()
      .subscribe((importEvent) => {
        if (importEvent.type === HttpEventType.UploadProgress) {
          this.uploadPercentDone = Math.round((100 * importEvent.loaded) / importEvent.total);
        } else if (importEvent instanceof HttpResponse) {
          let data = (importEvent.body as any) || importEvent;
          this.importData = { ...this.importData, ...data };
          this.setStep();
          this.checkImport(this.importData.id_import);
        }
      });
  }

  checkImport(id_import) {
    if (this.isDestroyed) {
      return;
    }
    this._subs['check_import'] = this._mData
      .getOne('MODULATOR', 'modules.import', id_import, { fields: this.apiFields })
      .subscribe((data) => {
        this.importData = { ...this.importData, ...data };
        this.setStep();
        if (['PROCESSING', 'STARTING'].includes(this.importData.status)) {
          setTimeout(() => this.checkImport(id_import), 1000);
        }
        if (['DONE', 'PENDING', 'ERROR'].includes(this.importData.status)) {
          this._mLayout.stopActionProcessing('');
        }
        if (this.importData.status == 'DONE') {
          if (this.importData.res.nb_unchanged != this.importData.res.nb_process) {
            this._mObject.reProcessObject(this.context.module_code, this.context.object_code);
          }
        }
      });
  }

  processAction(event: any): void {
    const { action, context, value = null, data = null, layout = null } = event;
    if (action == 'import') {
      return this.processImport(context, data);
    }
    if (action == 'reset') {
      this._mLayout.getFormControl('form_import')?.reset();
      this.initImport();
      this._mLayout.stopActionProcessing('');
      setTimeout(() => {
        this._mLayout.reComputeLayout('');
      }, 50);
    }
  }
}
