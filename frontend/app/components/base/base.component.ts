import { Component, OnInit, Input, Output, EventEmitter, SimpleChanges } from "@angular/core";
import { ActivatedRoute, Router, ParamMap } from "@angular/router";
import { ModulesConfigService } from "../../services/config.service";
import { ModulesDataService } from "../../services/data.service";
import { CommonService } from "@geonature_common/service/common.service";
import { ModulesMapService } from "../../services/map.service"
import { ModulesFormService } from "../../services/form.service"

import { mergeMap, concatMap, catchError } from "@librairies/rxjs/operators";
import { Observable, of, forkJoin } from "@librairies/rxjs";
import utils  from "../../utils"
import { ModulesRouteService } from "../../services/route.service";

@Component({
  selector: "modules-base-component",
  template: "",
})
export class BaseComponent implements OnInit {

  @Input() schemaName: string = null;
  @Input() moduleName: string = null;
  @Input() debug: boolean = false;
  @Input() value = null;

  @Input() filters = [];

  @Input() mapId: string = null;
  @Input() height: string = "600px";
  @Input() zoom: number = null;
  @Input() center: Array<number> = null;

  @Input() displayTitle=false;
  @Input() displayFilters=false;
  @Input() short: boolean = false;
  @Input() size;
  @Input() actions;

  @Input() layout;
  @Input() layoutData;

  @Output() onEvent: EventEmitter<any> = new EventEmitter<any>();


  processedEntries = ['moduleName', 'schemaName', 'value', 'filters'];

  componentInitialized = false;
  isProcessing=false;

  response = null;
  data = null;
  layersData = null;

  fields;

  schemaConfig = null;
  moduleConfig = null;

  componentTitle = null;

  errorMsg = null;

  _name: string;

  constructor(
    protected _route: ActivatedRoute,
    protected _commonService: CommonService,
    protected _mapService: ModulesMapService,
    protected _mConfig: ModulesConfigService,
    protected _mData: ModulesDataService,
    protected _mForm: ModulesFormService,
    protected _router: Router,
    protected _mRoute: ModulesRouteService,
  ) {
    this._name = 'BaseComponent';
  }

  ngOnInit() {
    this.process();
  }

  id() {
    return this.data[this.schemaConfig.utils.pk_field_name];
  }

  emitEvent(event) {
    this.onEvent.emit(event);
    setTimeout(()=> {});
  }

  getLayoutFields(layout) {
    if (this.getLayoutType(layout) == 'array') {
      return utils.flat(layout.map(l => this.getLayoutFields(l)))
    }
    if (this.getLayoutType(layout) == 'obj') {
      return utils.flat(layout.items.map(l => this.getLayoutFields(l)))
    }
    return layout.key || layout;
  };

  getLayoutType(layout) {
    return !layout
      ? null
      : Array.isArray(layout)
        ? 'array'
        : utils.isObject(layout) && layout.items
          ? 'obj'
          : 'key'
  };

  geometryFieldName() {
    return this.schemaConfig.utils.geometry_field_name;
  }

  hasGeometry() {
    return !!this.geometryFieldName();
  }


  labelFieldName() {
    return this.schemaConfig.utils.label_field_name;
  }

  pkFieldName() {
    return this.schemaConfig.utils.pk_field_name;
  }

  setComponentTitle() {}

  deepEqual(elem1, elem2) {
    return utils.fastDeepEqual(elem1, elem2);
  }

  log(msg) {
    console.log(`${this._name}`, msg)
  }

  process() {
    this.mapId = this.mapId || `map_${Math.random()}`;

    if(this.isProcessing) {
      return;
    }
    this.isProcessing = true;
    // load_config
    this._mConfig
      .loadConfig(this.schemaName)
      .pipe(
        mergeMap((schemaConfig) => {
          this.schemaConfig=schemaConfig;
          this.moduleConfig=this._mConfig.moduleConfig(this.moduleName);
          this.processConfig();
          return of(true);
        }),
        // catchError(error => {
        //   this.errorMsg = error;
        //   return of(console.error()
        // }),
        mergeMap(() => {
          return this.getData()
        }),
        catchError((error) => {
          this.isProcessing=false;
          this.componentInitialized = true;
          return of(false)
        })
      ).subscribe((response) => {
          if(response) {
            this.processData(response);
          }
          this.setComponentTitle();
          this.isProcessing=false;
          this.componentInitialized = !!response;
          this.onComponentInitialized()
          });
    }

  onComponentInitialized() {}

  processConfig() {}

  /**
   * A reimplémenter dans les composants
   * Ce que l'on fait des données que l'on vient de récupérer
   */
  processData(response) {
    // console.error("processData doit être réimplémenté")
  }

  /**
   * A reimplémenter dans les composants
   * Comment récupérer les données
   */
   getData(): Observable<any> {
    // console.error("getData doit être réimplémenté")
    return of(true);
  }

  setQueryParams(queryParams) {
      const queryParamsProcessed = {};
      for (const [key, value] of Object.entries(queryParams) ){
        queryParamsProcessed[key] = (Array.isArray(value) || utils.isObject(value))
          ? JSON.stringify(value)
          : value
      }
      this._router.navigate([], {
      relativeTo: this._route,
      queryParams: queryParamsProcessed,
      queryParamsHandling: 'merge',
    });
  }

  ngOnChanges(changes: SimpleChanges): void {
    for (const [key, change] of Object.entries(changes)) {

      if(utils.fastDeepEqual(change['currentValue'], change['previousValue'])) {
        continue;
      }

      if(this.processedEntries.includes(key)) {
        this.process();
      }
    }
  }
}
