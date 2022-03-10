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

  // patch pour que les fieldset puissent etre en colonne
  processFieldSets(elemId) {
    utils.waitForElement(elemId).then((container) => {
      utils.waitForElements(
        '.fieldset-column > flex-layout-root-widget',
        container
        ).then((elems) => {
          for (let elem of (elems as Array<any>)) {
            elem.style['flex-direction'] = 'column';
            elem.style['flex-flow'] = 'column';
          }
        });
      });
  }

  processLayout(layout) {

    if ( Array.isArray(layout) ) {
      return layout.map(l => this.processLayout(l))
    }

    else if ( utils.isObject(layout) ) {
      // layout.fxLayoutGap = '1px';

      if (layout.type == 'fieldset') {
        layout.htmlClass+=' fieldset';
      }

      if (['fieldset', 'array'].includes(layout.type)) {
        if ( layout.direction == 'row') {
        } else {
          layout.htmlClass+=' fieldset-column';
      }
      }

      if ( layout.direction == 'row') {
        layout.displayFlex = true;
        layout['flex-direction'] = 'row';
        layout.fxLayoutGap = '5px';

      }
      for (const [key, value] of Object.entries(layout)) {
        if(! ['params'].includes(key)) {
          layout[key] = this.processLayout(value)
        }
      }
      return layout;
    }

    else {
      // layout.fxLayoutGap = '5px';
      return layout;
    }

  }

}