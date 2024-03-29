import { Component, OnInit, Injector, Input } from '@angular/core';
import { ModulesDataService } from '../../../services/data.service';

import { ModulesLayoutComponent } from './layout.component';
@Component({
  selector: 'modules-layout-breadcrumbs',
  templateUrl: 'layout-breadcrumbs.component.html',
  styleUrls: ['../../base/base.scss', 'layout-breadcrumbs.component.scss'],
})
export class ModulesLayoutBreadcrumbsComponent extends ModulesLayoutComponent implements OnInit {
  /** options pour les elements du array */

  // arrayOptions: Array<any>;

  breadcrumbs: any;
  _mData: ModulesDataService;
  _injector: Injector;

  constructor(_injector: Injector) {
    super(_injector);
    this._name = 'layout-breadcrumbs';
    this.bPostComputeLayout = true;
    this._mData = this._injector.get(ModulesDataService);
  }

  postComputeLayout(dataChanged: any, layoutChanged: any, contextChanged: any): void {
    if (contextChanged) {
      this._subs['breadcrumbs'] = this._mData
        .getBreadcrumbs(this.context)
        .subscribe((breadcrumbs) => {
          this.breadcrumbs = breadcrumbs;
          this._subs['breadcrumbs'].unsubscribe();
        });
    }
  }
}
