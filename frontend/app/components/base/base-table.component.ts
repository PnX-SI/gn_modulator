import { Component, OnInit, Input, SimpleChanges } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { ActivatedRoute, Router, ParamMap } from "@angular/router";
import { ModulesConfigService } from "../../services/config.service"
import { ModulesDataService } from "../../services/data.service"
import { mergeMap, concatMap } from "@librairies/rxjs/operators";
import { Observable, of, forkJoin } from "@librairies/rxjs";
import Tabulator from "tabulator-tables";

@Component({
  selector: "modules-base-table",
  templateUrl: "base-table.component.html",
  styleUrls: ["base-table.component.scss"],
})
export class BaseTableComponent implements OnInit {


  @Input() moduleCode = null;
  @Input() schemaName = null;
  @Input() value = null;

  componentInitialized = false;
  schemaConfig = null;
  tableTitle = null;
  data = null;

  columnNames: any[] = [
    { title: "ID", field: "id_example", headerFilter: true },
    { title: "Nom", field: "example_name", headerFilter: true },
    { title: "Code", field: "example_code", headerFilter: true },
  ];
;

  public table;
  public height: string = "311px";
  tab = document.createElement("div");

  constructor(
    private _route: ActivatedRoute,
    private _mConfig: ModulesConfigService,
    private _mData: ModulesDataService
  ) {}


  ngOnInit() {

    // load_config
    this.process();
  }

  process() {
    // load_config
    this._mConfig.loadConfig(this.moduleCode, this.schemaName)
      .pipe(
        mergeMap((schemaConfig) => {
          this.schemaConfig = schemaConfig; 
          return of(true)
        }),
        mergeMap(() => {
          return this._mData.getOne(this.moduleCode, this.schemaName, this.value)
        }),
        mergeMap((data) => {
          this.data = data;
          this.setTableTitle();

          return of(true)
        })
      ).subscribe(() => {
        this.componentInitialized = true;
        this.drawTable()
      });
  }

  columns() {
    return this.schemaConfig.utils.properties_array
      .map(p => ({title: p.label, field: p.name, headerFilter: true}))
  }

  drawTable(): void {
    this.table = new Tabulator(this.tab, {
      height: "311px",
      layout: "fitColumns",
      placeholder: "No Data Set",
      ajaxFiltering: true,
      columns: this.columns(),
      ajaxURL: this.schemaConfig.utils.urls.rest,
      ajaxURLGenerator: function (url, config, params) {
        return url + "?params=" + encodeURI(JSON.stringify(params)); //encode parameters as a json object
      },
      paginationSize: 5,
      pagination: "remote",
      ajaxSorting: true,
    });
    document.getElementById("my-tabular-table").appendChild(this.tab);
  }

  id() {
      return this.data[this.schemaConfig.utils.pk_field_name];
  }

  setTableTitle() {
      this.tableTitle = this.schemaConfig.display.undef_labels;
  }

  ngOnChanges(changes: SimpleChanges): void {
    this.process();
  }

}

