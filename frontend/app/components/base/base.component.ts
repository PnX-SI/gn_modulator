import {
  Component,
  OnInit,
  Input,
  Output,
  EventEmitter,
  SimpleChanges,
} from "@angular/core";

import { ModulesService } from "../../services/all.service";

import { User } from "@geonature/components/auth/auth.service";
import { mergeMap, catchError } from "@librairies/rxjs/operators";
import { Observable, of } from "@librairies/rxjs";
import utils from "../../utils";

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

  @Input() displayTitle = false;
  @Input() displayFilters = false;
  @Input() short: boolean = false;
  @Input() size;
  @Input() actions;

  @Input() layout;
  @Input() layoutData;
  @Output() onEvent: EventEmitter<any> = new EventEmitter<any>();

  processedEntries = ["moduleName", "schemaName", "value", "filters"];

  componentInitialized = false;
  isProcessing = false;

  response;
  data;
  layersData;

  fields;

  elemId;

  schemaConfig;
  moduleConfig;

  componentTitle;

  errorMsg;

  heightDec = 20;
  _name: string;

  currentUser: User;

  constructor(protected _services: ModulesService) {
    this._name = "BaseComponent";
    this.elemId = `elem_${Math.random()}`.replace(".", "");
  }

  ngOnInit() {
    this.process();
  }

  setFullHeight() {
    utils.waitForElement(this.elemId).then((elem) => {
      const height =
        document.body.clientHeight -
        document.getElementById(this.elemId).offsetTop;
      this.height = height - this.heightDec + "px";
      this.afterResize();
    });
    // document.getElementById("object").style.height = height - 20 + "px";

    // this.heightMap = height - 60 + "px";
  }

  afterResize() {}

  listenResize() {
    window.addEventListener(
      "resize",
      (event) => {
        this.setFullHeight();
      },
      true
    );
  }

  initHeight(dec = null) {
    this.heightDec = dec || this.heightDec;
    this.setFullHeight();
    this.listenResize();
  }

  id() {
    return this.data[this.schemaConfig.utils.pk_field_name];
  }

  label() {
    return this.data[this.schemaConfig.utils.label_field_name];
  }

  emitEvent(event) {
    this.onEvent.emit(event);
    setTimeout(() => {});
  }

  geometryFieldName() {
    return this.schemaConfig.utils.geometry_field_name;
  }

  geometryType() {
    if (!this.hasGeometry()) {
      return;
    }
    return this.schemaConfig.definition.properties[this.geometryFieldName()]
      .geometry_type;
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
    console.log(`${this._name} ${this.elemId}`, msg);
  }

  process() {
    this.currentUser = this._services.auth.getCurrentUser();

    this.mapId = this.mapId || `map_${Math.random()}`;

    if (this.isProcessing) {
      return;
    }
    this.isProcessing = true;
    // load_config
    this._services.mConfig
      .loadConfig(this.schemaName)
      .pipe(
        mergeMap((schemaConfig) => {
          this.schemaConfig = schemaConfig;
          this.moduleConfig = this._services.mConfig.moduleConfig(
            this.moduleName
          );
          this.processConfig();
          return of(true);
        }),
        // catchError(error => {
        //   this.errorMsg = error;
        //   return of(console.error()
        // }),
        mergeMap(() => {
          return this.getData();
        }),
        catchError((error) => {
          this.isProcessing = false;
          this.componentInitialized = true;
          return of(false);
        })
      )
      .subscribe((response) => {
        if (response) {
          this.processData(response);
        }
        this.setComponentTitle();
        this.isProcessing = false;
        this.componentInitialized = !!response;
        this.onComponentInitialized();
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
    for (const [key, value] of Object.entries(queryParams)) {
      queryParamsProcessed[key] =
        Array.isArray(value) || utils.isObject(value)
          ? JSON.stringify(value)
          : value;
    }
    this._services.router.navigate([], {
      relativeTo: this._services.route,
      queryParams: queryParamsProcessed,
      queryParamsHandling: "merge",
    });
  }

  exportUrl(exportCode) {
    const exportConfig = this.moduleConfig.exports.find(
      (c) => c.export_code == exportCode
    );
    return this._services.request.url(this.schemaConfig.utils.urls.rest, {
      ...exportConfig,
      filters: this._services.schema.get(this.schemaName).filters,
    });
  }

  ngOnChanges(changes: SimpleChanges): void {
    for (const [key, change] of Object.entries(changes)) {
      if (
        utils.fastDeepEqual(change["currentValue"], change["previousValue"])
      ) {
        continue;
      }

      if (this.processedEntries.includes(key)) {
        this.process();
      }
    }
  }
}
