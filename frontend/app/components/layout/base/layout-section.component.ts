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
  selectedIndex;

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
      ? items.map((item) => {
          if (!utils.isObject(item)) {
            return item;
          }
          const computedItem = {};
          for (const key of ['label', 'hidden', 'disabled']) {
            computedItem[key] = this._mLayout.evalLayoutElement({
              element: item[key],
              layout: item,
              data: this.data,
              context: {
                ...this.context,
                object_code: item.object_code,
              },
            });
          }
          return computedItem;
        })
      : [];

    // pour les tabs
    // - si computedLayout.tab
    //    alors on choisi cet onglet par defaut
    setTimeout(() => {
      if (this.computedLayout.display == 'tabs' && this.computedLayout.selected_tab) {
        this.selectedIndex = this.computedItems.findIndex(
          (i) => i.label == this.computedLayout.selected_tab
        );
        console.log(this.selectedIndex);
      }
    }, 100);
  }
}
