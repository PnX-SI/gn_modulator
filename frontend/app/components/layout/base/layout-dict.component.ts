import { Component, OnInit, Injector } from '@angular/core';
import { ModulesFormService } from '../../../services/form.service';

import { ModulesLayoutComponent } from './layout.component';
@Component({
  selector: 'modules-layout-dict',
  templateUrl: 'layout-dict.component.html',
  styleUrls: ['../../base/base.scss', 'layout-dict.component.scss'],
})
export class ModulesLayoutDictComponent extends ModulesLayoutComponent implements OnInit {
  /** options pour les elements du array */

  // arrayOptions: Array<any>;

  _formService;
  constructor(_injector: Injector) {
    super(_injector);
    this._formService = this._injector.get(ModulesFormService);
    this._name = 'layout-object';
  }

  objectOptions() {
    return {
      ...this.options,
      formGroup: this.options.formGroup && this.options.formGroup.get(this.layout.key),
    };
  }
}
