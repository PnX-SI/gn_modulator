import { Component, OnInit, Input, SimpleChanges } from "@angular/core";
import { ActivatedRoute, Router, ParamMap } from "@angular/router";
import { ModulesConfigService } from "../services/config.service";
import { ModulesMapService } from "../services/map.service";
import { mergeMap, concatMap } from "@librairies/rxjs/operators";
import { Observable, of, forkJoin } from "@librairies/rxjs";

@Component({
  selector: "modules-test",
  templateUrl: "test.component.html",
  styleUrls: ["test.component.scss"],
})
export class TestComponent implements OnInit {

  componentInitialized = false;

  // route parameters
  schemaName = null;
  debug = false;
  value = null;
  tab = null;

  listTab=[];
  activeTab=null;
  tabIndex = 0;


  mapListId='mapList';
  mapEditId='mapEdit';
  mapDetailId='mapDetail';
  height='600px';
  zoom = null;
  center = null;

  filters = {}

  constructor(
    private _route: ActivatedRoute,
    private _router: Router,
    protected _mapService: ModulesMapService,
    private _mConfig: ModulesConfigService,
  ) {}

  ngOnInit() {
    this.process();
    this._mapService.waitForMap(this.mapListId).then((map) => {
      (map as any).on('zoomend', () => { this.setMapQueryParams(this.mapListId) });
      (map as any).on('moveend', () => { this.setMapQueryParams(this.mapListId) });
    })
  }

  setMapQueryParams(mapId) {
    this.zoom = this._mapService.getZoom(mapId);
    this.center = this._mapService.getCenter(mapId, true);
    this.setQueryParams({
      zoom: this.zoom,
      center: this.center
    })
  }
  /**
   * Chargement de la configuration
   */
  process() {
    this._route.queryParams
    .pipe(
      mergeMap((params) => {
        this.schemaName = params.schemaName;
        this.value = params.value;
        this.tab = params.tab;
        this.debug = ![undefined, false, 'false'].includes(params.debug);
        this.filters = JSON.parse(params.filters || 'null');
          // pour eviter d'avoir des strings
        this.zoom = params.zoom && Number(params.zoom);
        this.center = params.center
          ? params.center.map(c => Number(c))
          : null
        ;
        return this._mConfig.loadConfig(this.schemaName)
      }),
      mergeMap(() => {
        this.listTab = this._mConfig.schemaConfig(this.schemaName).utils.geometry_field_name
          ? ['map', 'table', 'detail', 'edit', 'filters', ]
          : ['table', 'detail', 'edit', 'filters']
        ;
        return of(true)
      }),
    ).subscribe(() => {
      this.componentInitialized = true;
      if(![null, undefined].includes(this.tab)) {
        this.tabIndex = this.listTab.indexOf(this.tab);
      }

    });
  }

  onLayerClick(event) {
    this.value = event.value;
    this.setQueryParams({
      value: event.value,
    });
  }

  onRowSelected(event) {
    this.value = event.value;

    if (this.listTab.includes(event.action)) {
      this.tabIndex = this.listTab.indexOf(event.action);

    }
    this.setQueryParams({
      value: event.value,
      tab: event.action
    });

  }

  setQueryParams(queryParams) {
      this._router.navigate([], {
       relativeTo: this._route,
       queryParams,
       queryParamsHandling: 'merge',
    });
  }

  onTabChange(event) {
    this.setQueryParams({tab: this.listTab[event.index]});
  }

}
