import { Component, OnInit, Injector, ViewChild } from '@angular/core';
import { ModulesLayoutComponent } from './layout.component';
import { MatTabGroup } from '@angular/material/tabs';

import utils from '../../../utils';

@Component({
  selector: 'modules-layout-section',
  templateUrl: 'layout-section.component.html',
  styleUrls: ['../../base/base.scss', 'layout-section.component.scss'],
})
export class ModulesLayoutSectionComponent extends ModulesLayoutComponent implements OnInit {
  constructor(_injector: Injector) {
    super(_injector);
    this._name = 'layout-section';
  }

  preProcessContext(): void {
    if (this.layout.key) {
      utils.addKey(this.context.data_keys, this.layout.key);
    }
  }
}
