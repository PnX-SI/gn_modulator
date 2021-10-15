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
  @Input() groupName = null;
  @Input() objectName = null;
  @Input() value = null;

  componentInitialized = false;
  schemaConfig = null;
  data = null;
  dataSource = null;
  displayedColumns = null;
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
      .loadConfig(this.groupName, this.objectName)
      .pipe(
        mergeMap((schemaConfig) => {
          this.schemaConfig = schemaConfig;
          return of(true);
        }),
        mergeMap(() => {
          return this._mData.getOne(
            this.groupName,
            this.objectName,
            this.value
          );
        }),
    //     <tr *ngFor="let prop of schemaConfig.utils.properties_array">
    //     <th>{{ prop.name }}</th>
    //     <td>{{ prop.label }}</td>
    //     <td>{{ prop.type }}</td>
    //     <td>{{ data[prop.name] }}</td>
    //  </tr>

        mergeMap((data) => {
          this.data = data;
          this.dataSource = this.schemaConfig.utils.properties_array.map(
            p => ({
              name: p.name,
              label: p.label,
              type: p.type,
              value: data[p.name]
            })
          );
          this.displayedColumns = ['name', 'label', 'type', 'value']
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
