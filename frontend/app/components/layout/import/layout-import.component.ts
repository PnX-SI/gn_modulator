import { Component, OnInit, Injector, ViewEncapsulation, ViewChild } from '@angular/core';
import { ModulesLayoutComponent } from '../base/layout.component';
import { ModulesImportService } from '../../../services/import.service';
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

  step = 0;

  uploadPercentDone;

  editableStep = false;

  importMsg: any = {};

  importDataTest = {
    // status: 'READY',
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

  @ViewChild('stepper') stepper: MatStepper;

  constructor(_injector: Injector) {
    super(_injector);
    this._name = 'layout-import';
    this.bPostComputeLayout = true;
    this._mImport = this._injector.get(ModulesImportService);
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
    this.importData = this.computedLayout.test_import ? this.importDataTest : {};
    this.setStep();
  }

  setStep() {
    // this.editableStep = true;
    this.step = this.importData.status == 'READY' ? 1 : this.importData.status == 'DONE' ? 2 : 0;

    if (this.stepper) {
      this.editableStep = true;
      setTimeout(() => {
        const diff = this.step - this.stepper.selectedIndex;
        for (let i = 0; i < Math.abs(diff); i++) {
          if (diff > 0) {
            this.stepper.next();
          }
          if (diff < 0) {
            this.stepper.previous();
          }
        }
        this.editableStep = false;
      });
    }
    this.importData.importMsg = this._mImport.processMessage(this.importData);
    this.importData.errorMsgType = this._mImport.processErrorsType(this.importData);
    this.importData.errorMsgLine = this._mImport.processErrorsLine(this.importData);
  }

  processImport(context, data) {
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
          this.importData = { ...this.importData, ...response };
          this.setStep();
          if (response.status == 'DONE') {
            if (response.res.nb_unchanged != response.res.nb_process) {
              this._mObject.reProcessObject(this.context.module_code, this.context.object_code);
            }
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
    }
  }
}
