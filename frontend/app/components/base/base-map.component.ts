import { Component, OnInit, Input, SimpleChanges, Output, EventEmitter } from "@angular/core";
import { ActivatedRoute, Router, ParamMap } from "@angular/router";
import { ModulesConfigService } from "../../services/config.service"
import { ModulesDataService } from "../../services/data.service"
import { mergeMap, concatMap } from "@librairies/rxjs/operators";
import { Observable, of, forkJoin } from "@librairies/rxjs";
import tabulatorLangs  from './utils-table/tabulator-langs'
import Tabulator from "tabulator-tables";

@Component({
  selector: "modules-base-map",
  templateUrl: "base-map.component.html",
  styleUrls: [ "base-map.component.scss", ],
})
export class BaseMapComponent implements OnInit {

  @Input() groupName = null;
  @Input() objectName = null;
  @Input() value = null;
  @Input() filters = [];

  @Output() onLayerClick: EventEmitter<any> = new EventEmitter<any>();

  componentInitialized = false;
  schemaConfig = null;
  mapTitle = null;
  geoms = null;

  heightMap='1000px'

  constructor(
    private _route: ActivatedRoute,
    private _mConfig: ModulesConfigService,
    private _mData: ModulesDataService
  ) { }

  ngOnInit() {
    // load_config
    this.process();
  }

  process() {
    // load_config
    this._mConfig.loadConfig(this.groupName, this.objectName)
      .pipe(
        mergeMap((schemaConfig) => {
          this.componentInitialized = false;
          this.schemaConfig = schemaConfig;
          return of(true)
        }),
      ).subscribe(() => {
        this.setMapTitle();
        this.componentInitialized = true;
        // wait for element #my-tabular-table
        setTimeout(()=> {
          this.getData()
        }, 100);
      });
  }

  onEachFeature = (feature, layer) => {
  }

  getData = () => {
      const fields = this.schemaConfig.table.columns.map(column => column.field);
      const extendedParams = {
        fields: ['id_pf', 'nom_pf', 'x', 'y'], // fields
        filters: this.filters,
        as_geojson: true,
        size: 100000,
      };
      this._mData.getList(this.groupName, this.objectName, extendedParams).subscribe((res) => {

          this.geoms = res['data'].map((r) => {
            return {
              type: 'Feature',
              "geometry": {
                "type": "Point",
                "coordinates": [r.x, r.y]
              }
            }
          });
    });
  }

  setMapTitle() {
      this.mapTitle = `Carte ${this.schemaConfig.display.undef_labels}`;
  }

  ngOnChanges(changes: SimpleChanges): void {
    this.process();
  }

}

