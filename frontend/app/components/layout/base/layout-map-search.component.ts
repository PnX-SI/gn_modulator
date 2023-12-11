import { Component, OnInit, Input, Injector, ViewEncapsulation } from '@angular/core';
import { ModulesMapService } from '../../../services/map.service';
import { Map, LatLngExpression, LatLngBounds } from 'leaflet';
import { NominatimService } from '@geonature_common/map/map.component';
import { CommonService } from '@geonature_common/service/common.service';
import { UntypedFormControl } from '@angular/forms';
import { Observable, of } from 'rxjs';
import {
  catchError,
  debounceTime,
  distinctUntilChanged,
  tap,
  switchMap,
  map,
} from 'rxjs/operators';

@Component({
  selector: 'modules-layout-map-search',
  templateUrl: 'layout-map-search.component.html',
  styleUrls: ['layout-map-search.component.scss', '../../base/base.scss'],
  encapsulation: ViewEncapsulation.None,
  providers: [NominatimService],
})
export class ModulesLayoutMapSearchComponent implements OnInit {
  _mapService: ModulesMapService;
  @Input() mapId; // identifiant HTML pour la table;

  _nominatim: NominatimService;
  _commonService: CommonService;

  public searching = false;
  public searchFailed = false;

  public locationControl = new UntypedFormControl();

  constructor(protected _injector: Injector) {
    this._mapService = this._injector.get(ModulesMapService);
    this._nominatim = this._injector.get(NominatimService);
    this._commonService = this._injector.get(CommonService);
  }

  ngOnInit() {}

  search = (text$: Observable<string>) =>
    text$.pipe(
      debounceTime(300),
      distinctUntilChanged(),
      tap(() => (this.searching = true)),
      switchMap((term) =>
        this._nominatim.search(term).pipe(
          tap(() => (this.searchFailed = false)),
          catchError(() => {
            this._commonService.translateToaster('Warning', 'Map.LocationError');
            this.searchFailed = true;
            return of([]);
          }),
        ),
      ),
      tap(() => (this.searching = false)),
    );

  onResultSelected(nomatimObject) {
    let bounds: LatLngBounds;
    if (nomatimObject.item?.geojson) {
      const geojson = this._mapService.L.geoJSON(nomatimObject.item.geojson);
      bounds = geojson.getBounds();
    } else {
      const boundingBox: number[] = nomatimObject.item.boundingbox;
      bounds = this._mapService.L.latLngBounds(
        this._mapService.L.latLng(boundingBox[0], boundingBox[2]),
        this._mapService.L.latLng(boundingBox[1], boundingBox[3]),
      );
    }
    this._mapService.getMap(this.mapId).fitBounds(bounds);
  }

  formatter(nominatim) {
    return nominatim.display_name;
  }
}
