import { Component, OnInit } from '@angular/core';
import { ModulesConfigService } from '../services/config.service';
import { ModulesRouteService } from '../services/route.service';

@Component({
  selector: 'modules-index',
  templateUrl: 'index.component.html',
  styleUrls: ['index.component.scss'],
})
export class ModulesIndexComponent implements OnInit {
  schemaGroups = {};
  groups = [];
  modules;
  layout: {};

  _sub;

  constructor(
    private _mConfig: ModulesConfigService,
    private _mRoute: ModulesRouteService,
  ) {}
  ngOnInit() {
    this._sub = this._mConfig.init().subscribe(() => {
      const modules = this._mConfig.modulesConfig();
      this.modules = Object.values(modules).filter(
        (m) => (m as any).code != this._mConfig.MODULE_CODE,
      );
      this.layout = {
        title: 'Liste des modules',
        class: 'modules',
        height_auto: true,
        items: [
          {
            overflow: true,
            items: {
              direction: 'row',
              class: 'modules-liste',
              items: this.modules
                .filter((moduleConfig) => moduleConfig.registred)
                .map((moduleConfig) => ({
                  flex: 'inherit',
                  title: moduleConfig.module.module_label,
                  description: moduleConfig.module.module_desc,
                  href: '/' + moduleConfig.module.module_path,
                  img: this._mConfig.moduleImg(moduleConfig.code),
                  type: 'card',
                  class: 'module-card',
                })),
            },
          },
        ],
      };
    });
  }

  ngOnDestroy() {
    this._sub && this._sub.unsubscribe();
  }
}
