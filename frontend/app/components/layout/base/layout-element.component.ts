import { Component, OnInit, Injector } from '@angular/core';
import { ModulesLayoutComponent } from './layout.component';

@Component({
  selector: `modules-layout-element`,
  templateUrl: 'layout-element.component.html',
  styleUrls: ['../../base/base.scss', 'layout-element.component.scss'],
})
export class ModulesLayoutElementComponent extends ModulesLayoutComponent implements OnInit {
  constructor(_injector: Injector) {
    super(_injector);
    this._name = 'layout-element';
  }
}
