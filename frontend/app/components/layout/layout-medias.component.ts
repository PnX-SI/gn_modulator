import { Component, OnInit } from "@angular/core";
import { ModulesLayoutService } from "../../services/layout.service";
import { ModulesLayoutComponent } from "./layout.component";
import { MediaService } from '@geonature_common/service/media.service';

@Component({
  selector: "modules-layout-medias",
  templateUrl: "layout-medias.component.html",
  styleUrls: ["../base/base.scss", "layout-medias.component.scss"],
})
export class ModulesLayoutMediasComponent
  extends ModulesLayoutComponent
  implements OnInit
{
  constructor(
    _mLayout: ModulesLayoutService,
    public ms: MediaService
  ) {
    super(_mLayout);
    this._name = "layout-medias";
  }
}
