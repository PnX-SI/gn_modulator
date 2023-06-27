import { Injectable, Injector } from '@angular/core';
import { ModulesDataService } from './data.service';
import { mergeMap, map, filter, switchMap } from 'rxjs/operators';
import { of } from 'rxjs';

@Injectable()
export class ModulesNomenclatureService {
  _nomenclatures: any[] = [];

  _mData: ModulesDataService;

  constructor(private _injector: Injector) {
    this._mData = this._injector.get(ModulesDataService);
    this.init().subscribe(() => {});
  }

  init() {
    if (this._nomenclatures.length) {
      return of(true);
    }
    return this._mData
      .dataRequest('get', 'MODULATOR', 'ref_nom.nomenclature', {
        params: { fields: ['id_nomenclature', 'cd_nomenclature'] },
      })
      .pipe(
        mergeMap((res) => {
          this._nomenclatures = res.data;
          return of(true);
        })
      );
  }

  get_cd_nomenclature(id_nomenclature) {
    if (!(this._nomenclatures.length && !!id_nomenclature)) {
      return;
    }
    let nomenclature = this._nomenclatures.find((n) => n.id_nomenclature == id_nomenclature);
    return nomenclature?.cd_nomenclature;
  }
}
