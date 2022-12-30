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

  postProcessContext(): void {
    if (this.layout.key) {
      utils.addKey(this.context.data_keys, this.layout.key);
    }
  }

  processItems() {
    const items = this.layoutType == 'items' ? this.layout : this.layout.items || [];

    this.computedItems = items.map
      ? items.map((item) =>
          this._mLayout.computeLayout({
            layout: item,
            data: this.data,
            context: { ...this.context, object_code: item.object_code },
          })
        )
      : [];
  }
}
