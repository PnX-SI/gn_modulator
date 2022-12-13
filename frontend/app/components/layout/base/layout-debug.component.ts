import { Component, OnInit, Input } from '@angular/core';

import utils from '../../../utils';

/** Composant de base pour les layouts */
@Component({
  selector: 'modules-layout-debug',
  templateUrl: 'layout-debug.component.html',
  styleUrls: ['../../base/base.scss', 'layout-debug.component.scss'],
})
export class ModulesLayoutDebugComponent implements OnInit {
  /** données */
  @Input() debugData: any;

  constructor() {}

  ngOnInit() {}
}
