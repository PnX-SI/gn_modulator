import { Component, OnInit, Injector } from '@angular/core';
import { ModulesFormService } from '../../../services/form.service';

import { ModulesLayoutComponent } from './layout.component';
@Component({
  selector: 'modules-layout-array',
  templateUrl: 'layout-array.component.html',
  styleUrls: ['../../base/base.scss', 'layout-array.component.scss'],
})
export class ModulesLayoutArrayComponent extends ModulesLayoutComponent implements OnInit {
  /** options pour les elements du array */

  // arrayOptions: Array<any>;

  constructor(private _formService: ModulesFormService, _injector: Injector) {
    super(_injector);
    this._name = 'layout-array';
    this.bPostComputeLayout = true;
  }

  arrayOptions(index) {
    return {
      ...this.options,
      index,
      formGroup: this.options.formGroup && this.options.formGroup.get(this.layout.key).at(index),
    };
  }

  processAction(action) {
    if (action.type == 'remove-array-element') {
      this.data[this.layout.key].splice(action.index, 1);
      this._formService.setControl(this.options.formGroup, this.layout, this.data, this.globalData);
      this._mLayout.reComputeLayout('');
    } else {
      this.emitAction(action);
    }
  }

  addArrayElement() {
    this.data[this.layout.key].push({});
    this._formService.setControl(this.options.formGroup, this.layout, this.data, this.globalData);
    // pour forcer le check de la validation ??
    this._mLayout.reComputeLayout('');
  }
}
