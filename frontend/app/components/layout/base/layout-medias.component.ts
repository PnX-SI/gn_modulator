import { Component, OnInit, Injector } from '@angular/core';
import { ModulesLayoutComponent } from './layout.component';
import { MediaService } from '@geonature_common/service/media.service';

@Component({
  selector: 'modules-layout-medias',
  templateUrl: 'layout-medias.component.html',
  styleUrls: ['../../base/base.scss', 'layout-medias.component.scss'],
})
export class ModulesLayoutMediasComponent extends ModulesLayoutComponent implements OnInit {
  ms;
  constructor(_injector: Injector) {
    super(_injector);
    this._name = 'layout-medias';
    this.ms = this._injector.get(MediaService);
  }
}
