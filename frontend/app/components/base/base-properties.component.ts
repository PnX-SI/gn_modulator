import { Component, OnInit, Input, SimpleChanges } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { ActivatedRoute, Router, ParamMap } from "@angular/router";
import { ModulesConfigService } from "../../services/config.service";
import { ModulesDataService } from "../../services/data.service";
import { mergeMap, concatMap } from "@librairies/rxjs/operators";
import { Observable, of, forkJoin } from "@librairies/rxjs";

@Component({
  selector: "modules-base-properties",
  templateUrl: "base-properties.component.html",
  styleUrls: ["base-properties.component.scss"],
})
export class BasePropertiesComponent implements OnInit {
  @Input() moduleCode = null;
  @Input() schemaName = null;
  @Input() value = null;

  componentInitialized = false;
  schemaConfig = null;
  data = null;

  constructor(
    private _route: ActivatedRoute,
    private _mConfig: ModulesConfigService,
    private _mData: ModulesDataService
  ) {}

  ngOnInit() {
    // load_config
    this.process();
  }

  id() {
    return this.data[this.schemaConfig.utils.pk_field_name];
  }

  process() {
    // load_config
    this._mConfig
      .loadConfig(this.moduleCode, this.schemaName)
      .pipe(
        mergeMap((schemaConfig) => {
          this.schemaConfig = schemaConfig;
          return of(true);
        }),
        mergeMap(() => {
          return this._mData.getOne(
            this.moduleCode,
            this.schemaName,
            this.value
          );
        }),
        mergeMap((data) => {
          this.data = data;
          return of(true);
        })
      )
      .subscribe(() => {
        this.componentInitialized = true;
      });
  }

  ngOnChanges(changes: SimpleChanges): void {
    this.process();
  }
}
