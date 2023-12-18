import { Component, OnInit, Injector, ViewEncapsulation, ViewChild } from '@angular/core';
import { ModulesLayoutComponent } from '../base/layout.component';
import { ModulesImportService } from '../../../services/import.service';
import { ModulesDataService } from '../../../services/data.service';
import { HttpEventType, HttpResponse, HttpErrorResponse } from '@angular/common/http';
import { MatStepper } from '@angular/material/stepper';

import utils from '../../../utils';

const _name = 'feature';
@Component({
  selector: `modules-layout-${_name}`,
  templateUrl: `layout-${_name}.component.html`,
  styleUrls: [`layout-${_name}.component.scss`, '../../base/base.scss'],
})
export class ModulesLayoutFeatureComponent extends ModulesLayoutComponent implements OnInit {
  featureData: any = {};
  featureLayout: any; // layout pour l'import de feature

  _mImport: ModulesImportService;
  _mData: ModulesDataService;

  constructor(_injector: Injector) {
    super(_injector);
    this._name = `layout-${_name}`;
    this._mImport = this._injector.get(ModulesImportService);
    this._mData = this._injector.get(ModulesDataService);
  }

  postInit(): void {
    this.featureLayout = {
      code: 'utils.feature',
    };
    this.featureData = {
      feature: `
- schema_code: ref_nom.nomenclature
  defaults:
    source: SIPAF
    active: true
  keys:
    [id_type, cd_nomenclature, mnemonique, label_default, definition_default]
  items:
    - [PF_OUVRAGE_MATERIAUX, BET, Bét., Béton, Béton]
    - [PF_OUVRAGE_MATERIAUX, MET, Mét., Métal, Métal]
    - [PF_OUVRAGE_MATERIAUX, PLT, Pla., Plastique, Plastique]
    - [PF_OUVRAGE_MATERIAUX, BOI, Boi., Bois, Bois]
    - [PF_OUVRAGE_MATERIAUX, MAC, Maç., Maçonnerie, Maçonnerie]
  `,
    };
  }

  processAction(event: any): void {
    const { action, context, value = null, data = null, layout = null } = event;
    if (action == 'feature') {
      let postData = utils.parseYML(data.feature);
      this._mImport.featureRequest(postData).subscribe((res) => {
        this.featureData.msg = res.msg;
        this._mLayout.reComputeLayout('post feature');
        this._mLayout.stopActionProcessing('post feature');
        console.log(this.featureData.msg);
      });
    }
  }
}
