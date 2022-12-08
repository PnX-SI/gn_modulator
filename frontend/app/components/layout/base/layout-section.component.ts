import { Component, OnInit, Injector } from '@angular/core';
import { ModulesLayoutComponent } from './layout.component';
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

  processDataKeys(): void {
    this.context.data_keys = utils.copy(this.parentContext.data_keys) || [];

    if (this.layout.key) {
      this.context.data_keys.push(this.layout.key);
    }
  }
}
