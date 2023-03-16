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

  @ViewChild('stepper') stepper: MatStepper;

  constructor(_injector: Injector) {
    super(_injector);
    this._name = 'layout-import';
    this.bPostComputeLayout = true;
    this._mImport = this._injector.get(ModulesImportService);
  }

  postComputeLayout() {
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
    this.importMsg = this._mImport.processMessage(this.importData);
    this.importData = {};
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
    this._mImport.processMessage(this.importData);
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
          this.importData = response;
          this.setStep();
        }
      });
  }

  processAction(event: any): void {
    const { action, context, value = null, data = null, layout = null } = event;
    if (action == 'import') {
      return this.processImport(context, data);
    }
    if (action == 'reset') {
      this.initImport();
      this._mLayout.stopActionProcessing('');
    }
  }
}
