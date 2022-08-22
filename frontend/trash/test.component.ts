import { Component, OnInit } from "@angular/core";
import { mergeMap } from "@librairies/rxjs/operators";
import { of } from "@librairies/rxjs";
import { ModulesService } from "../services/all.service";

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
    private _services: ModulesService
  ) {}

  ngOnInit() {
    this.process();
    this._services.mapService.waitForMap(this.mapListId).then((map) => {
      (map as any).on('zoomend', () => { this.setMapQueryParams(this.mapListId) });
      (map as any).on('moveend', () => { this.setMapQueryParams(this.mapListId) });
    })
  }

  setMapQueryParams(mapId) {
    this.zoom = this._services.mapService.getZoom(mapId);
    this.center = this._services.mapService.getCenter(mapId, true);
    this.setQueryParams({
      zoom: this.zoom,
      center: this.center
    })
  }
  /**
   * Chargement de la configuration
   */
  process() {
    this._services.route.queryParams
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
        return this._services.mConfig.loadConfig(this.schemaName)
      }),
      mergeMap(() => {
        this.listTab = this._services.mConfig.schemaConfig(this.schemaName).utils.geometry_field_name
          ? ['map', 'table', 'details', 'edit', 'filters', ]
          : ['table', 'details', 'edit', 'filters']
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
      this._services.router.navigate([], {
       relativeTo: this._services.route,
       queryParams,
       queryParamsHandling: 'merge',
    });
  }

  onTabChange(event) {
    this.setQueryParams({tab: this.listTab[event.index]});
  }

}
