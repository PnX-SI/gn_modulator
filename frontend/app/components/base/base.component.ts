import { Component, OnInit, Input, SimpleChanges } from "@angular/core";
import { ActivatedRoute, Router, ParamMap } from "@angular/router";
import { ModulesConfigService } from "../../services/config.service";
import { ModulesDataService } from "../../services/data.service";
import { CommonService } from "@geonature_common/service/common.service";
import { ModulesMapService } from "../../services/map.service"

import { mergeMap, concatMap, catchError } from "@librairies/rxjs/operators";
import { Observable, of, forkJoin } from "@librairies/rxjs";
import utils  from "../../utils"

@Component({
  selector: "modules-base-component",
  template: "",
})
export class BaseComponent implements OnInit {

  @Input() schemaName: string = null;
  @Input() debug: boolean = false;
  @Input() value = null;

  @Input() filters = [];

  @Input() mapId: string = null;
  @Input() heightMap: string = null;
  @Input() zoom: number = null;
  @Input() center: Array<number> = null;

  componentInitialized = false;
  isProcessing=false;
  schemaConfig = null;

  response = null;
  data = null;
  layersData = null;

  errorMsg = null;

  _name: string;

  constructor(
    protected _route: ActivatedRoute,
    protected _commonService: CommonService,
    protected _mapService: ModulesMapService,
    protected _mConfig: ModulesConfigService,
    protected _mData: ModulesDataService,
    protected _router: Router,
  ) {
    this._name = 'BaseComponent';
  }

  ngOnInit() {
    this.process();
  }

  id() {
    return this.data[this.schemaConfig.utils.pk_field_name];
  }

  geometryFieldName() {
    return this.schemaConfig.utils.geometry_field_name;
  }

  labelFieldName() {
    return this.schemaConfig.utils.label_field_name;
  }

  pkFieldName() {
    return this.schemaConfig.utils.pk_field_name;
  }

  deepEqual(elem1, elem2) {
    return utils.fastDeepEqual(elem1, elem2);
  }

  log(msg) {
    console.log(`${this._name} : ${msg}`)
  }

  process() {
    if(this.isProcessing) {
      return;
    }
    this.log('process')
    this.isProcessing = true;
    // load_config
    this._mConfig
      .loadConfig(this.schemaName)
      .pipe(
        mergeMap((schemaConfig) => {
          this.schemaConfig = schemaConfig;
          return of(true);
        }),
        // catchError(error => {
        //   this.errorMsg = error;
        //   return of(console.error()
        // }),
        mergeMap(() => {
          return this.getData()
        })
      ).subscribe((response) => {
          if(response) {
            this.processData(response);
          }
          this.isProcessing=false;
          this.componentInitialized = !!response;
          });
    }

  /**
   * A reimplémenter dans les composants
   * Ce que l'on fait des données que l'on vient de récupérer
   */
  processData(response) {
    console.error("processData doit être réimplémenté")
  }

  /**
   * A reimplémenter dans les composants
   * Comment récupérer les données
   */
   getData(): Observable<any> {
    console.error("getData doit être réimplémenté")
    return of(false);
  }

  setQueryParams(queryParams) {
      this._router.navigate([], {
      relativeTo: this._route,
      queryParams,
      queryParamsHandling: 'merge',
    });
  }

  ngOnChanges(changes: SimpleChanges): void {
    for (const [key, change] of Object.entries(changes)) {

      if(change['currentValue'] == change['previousValue']) {
        continue;
      }

      if(['schemaName', 'value'].includes(key)) {
        this.process();
      }
    }
  }
}
