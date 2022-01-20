import { Injectable } from "@angular/core";

import { AppConfig } from "@geonature_config/app.config";
import { ModuleConfig } from "../module.config";

import { of, Observable } from "@librairies/rxjs";
import { mergeMap, catchError } from "@librairies/rxjs/operators";
import { ModulesRequestService } from "./request.service";
import utils from "../utils"

@Injectable()
export class ModulesFormService {

  constructor(
  ) {}

  /** Configuration */

  init() {
  }

  processLayout(layout) {

    if ( Array.isArray(layout) ) {
      return layout.map(l => this.processLayout(l))
    }

    else if ( utils.isObject(layout) ) {
      layout.fxLayoutGap = '1px';

      if (layout.type == 'fieldset') {
        layout.htmlClass='fieldset';
      }

      if ( layout.direction == 'row') {
        // layout.type = 'flex';
        layout.displayFlex = true;
        layout.fxLayoutGap = '1px';
        layout['flex-direction'] = 'row';
      }
      for (const [key, value] of Object.entries(layout)) {
        if(! ['params'].includes(key)) {
          layout[key] = this.processLayout(value)
        }
      }
      return layout;
    }

    else {
      // layout['title'] = layout['title'] || layout['label'];
      return layout;
    }

  }

}