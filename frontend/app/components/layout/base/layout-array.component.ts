import { Component, OnInit, Injector } from '@angular/core';
import { ModulesFormService } from '../../../services/form.service';

import { ModulesLayoutComponent } from './layout.component';

import utils from '../../../utils';

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

  arrayItemsContext;

  postProcessContext() {
    if (!this.elementData) {
      return;
    }
    this.arrayItemsContext = this.elementData.map((d, index) => this.arrayItemContext(index));
  }

  arrayItemContext(index) {
    const data_keys = utils.copy(this.context.data_keys);
    utils.addKey(data_keys, `${this.layout.key}.${index}`);

    const arrayItemContext = {
      form_group_id: this.context.form_group_id,
      data_keys,
      index,
      debug: this.context.debug,
    };
    for (const key of Object.keys(this.context).filter(
      (key) => !['form_group_id', 'data_keys'].includes(key)
    )) {
      arrayItemContext[key] = this.context[key];
    }

    return arrayItemContext;
  }

  processAction(action) {
    if (action.type == 'remove-array-element') {
      this.localData[this.layout.key].splice(action.index, 1);
      this._mLayout.reComputeLayout('');
    } else {
      this.emitAction(action);
    }
  }

  addArrayElement() {
    this.localData[this.layout.key].push({});
    this._mLayout.reComputeLayout('');
  }
}
