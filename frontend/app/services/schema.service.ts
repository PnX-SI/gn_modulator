import { Injectable } from "@angular/core";

import { HttpClient } from "@angular/common/http";

import { Observable, Subject } from '@librairies/rxjs';
import { CommonService } from "@geonature_common/service/common.service";

@Injectable()
export class ModulesSchemaService {


  private _cache = {};

  constructor(
  ) {}

  get(schemaName) {
    if (!this._cache[schemaName]) {
      this._cache[schemaName] = {
        "filters": []
      }
    }
    return this._cache[schemaName];
  }

}