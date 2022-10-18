import { Component, OnInit, Injector, Input } from '@angular/core';
import { ModulesPageService } from '../../../services/page.service';

import { ModulesLayoutComponent } from './layout.component';
@Component({
  selector: 'modules-layout-breadcrumbs',
  templateUrl: 'layout-breadcrumbs.component.html',
  styleUrls: ['../../base/base.scss', 'layout-breadcrumbs.component.scss'],
})
export class ModulesLayoutBreadcrumbsComponent extends ModulesLayoutComponent implements OnInit {
  /** options pour les elements du array */

  // arrayOptions: Array<any>;
  _mPage: ModulesPageService;

  constructor(_injector: Injector) {
    super(_injector);
    this._name = 'layout-breadcrumbs';
    this.bPostComputeLayout = true;
    this._mPage = this._injector.get(ModulesPageService);
  }
}
