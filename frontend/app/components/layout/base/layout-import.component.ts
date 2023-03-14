import { Component, OnInit, Injector, ViewEncapsulation } from '@angular/core';
import { ModulesLayoutComponent } from './layout.component';
import { ModulesImportService } from '../../../services/import.service';

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

  processAction(event: any): void {
    const { action, context, value = null, data = null, layout = null } = event;
    if (action == 'import') {
      return this._mImport.processImport(context, data);
    }
  }
}
