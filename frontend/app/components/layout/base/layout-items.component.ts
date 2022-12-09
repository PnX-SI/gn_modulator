import { Component, OnInit, Injector, Input } from '@angular/core';
import { ModulesLayoutComponent } from './layout.component';
@Component({
  selector: 'modules-layout-items',
  templateUrl: 'layout-items.component.html',
  styleUrls: ['../../base/base.scss', 'layout-items.component.scss'],
})
export class ModulesLayoutItemsComponent extends ModulesLayoutComponent implements OnInit {
  constructor(_injector: Injector) {
    super(_injector);
    this._name = 'layout-items';
  }

  postProcessContext(): void {
    this.context.index = null;
  }

  processItems() {
    this.computedItems = this.layout.map((item) =>
      this._mLayout.computeLayout({
        layout: item,
        data: this.data,
        context: this.context,
      })
    );
  }
}
