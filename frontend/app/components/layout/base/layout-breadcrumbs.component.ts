import { Component, OnInit, Injector, Input } from '@angular/core';
import { ModulesDataService } from '../../../services/data.service';
import { ModulesContextService } from '../../../services/context.service';

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
  _mContext: ModulesContextService;
  _injector: Injector;

  constructor(_injector: Injector) {
    super(_injector);
    this._name = 'layout-breadcrumbs';
    this.bPostComputeLayout = true;
    this._mData = this._injector.get(ModulesDataService);
    this._mContext = this._injector.get(ModulesContextService);
  }

  postComputeLayout(dataChanged: any, layoutChanged: any): void {
    const context = this.context;
    this._mData
      .getBreadcrumbs(context)
      .subscribe((breadcrumbs) => (this.breadcrumbs = breadcrumbs));
  }
}
