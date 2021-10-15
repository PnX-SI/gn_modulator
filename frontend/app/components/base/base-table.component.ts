import { Component, OnInit, Input, SimpleChanges } from "@angular/core";
import { ActivatedRoute, Router, ParamMap } from "@angular/router";
import { ModulesConfigService } from "../../services/config.service"
import { ModulesDataService } from "../../services/data.service"
import { mergeMap, concatMap } from "@librairies/rxjs/operators";
import { Observable, of, forkJoin } from "@librairies/rxjs";
import tabulatorLangs  from './utils-table/tabulator-langs'
import Tabulator from "tabulator-tables";


@Component({
  selector: "modules-base-table",
  templateUrl: "base-table.component.html",
  styleUrls: [
    "../../../node_modules/tabulator-tables/dist/css/tabulator_site.min.css", //patch pour ne pas passer par angular.json
    "base-table.component.scss",
  ],
})
export class BaseTableComponent implements OnInit {

  @Input() groupName = null;
  @Input() objectName = null;
  @Input() value = null;

  componentInitialized = false;
  schemaConfig = null;
  tableTitle = null;
  data = null;

;

  public table;
  public height: string = "311px";
  tab = document.createElement("div");

  constructor(
    private _route: ActivatedRoute,
    private _mConfig: ModulesConfigService,
    private _mData: ModulesDataService
  ) {
  }



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
      ).subscribe((data) => {
        this.data = data;
        this.setTableTitle();

        this.componentInitialized = true;
        // wait for element #my-tabular-table
        setTimeout(()=> {
          this.drawTable()
        }, 100);
      });
  }

  ajaxRequestFunc = (url, config, params) => {
    return new Promise((resolve, reject) => {
      const fields = this.schemaConfig.table.columns.map(column => column.field);
      const extendedParams = {
        ...params, // depuis tabulator
        fields, // fields
      };
      this._mData.getList(this.groupName, this.objectName, extendedParams).subscribe((res) => {
        resolve(res);
        return;
      },
      (fail) => {
        reject(fail)
      });

    });
  }


  /**
   * fonction por gérer les paramètres de route des requêtes de liste
   */
  // ajaxURLGenerator = (url, config, params) => {

  //   /**
  //    * paramètre fields :
  //    *   - pour limiter les champs à récupérer
  //    *   - et alléger la requête
  //    */
  //   const fields = this.schemaConfig.table.columns.map(column => column.field);

  //   const extendedParams = {
  //     ...params, // depuis tabulator
  //     fields, // fields
  //   };
  //   return url + "?params=" + encodeURI(JSON.stringify(extendedParams)); //encode parameters as a json object
  // }

  drawTable(): void {
    this.table = new Tabulator(this.tab, {
      langs: tabulatorLangs,
      locale: 'fr',
      height: "311px",
      layout: "fitColumns",
      placeholder: "No Data Set",
      ajaxFiltering: true,
      ajaxRequestFunc: this.ajaxRequestFunc,
      columns: this.schemaConfig.table.columns,
      ajaxURL: this.schemaConfig.table.url,
      // ajaxURLGenerator: this.ajaxURLGenerator,
      paginationSize: 5,
      pagination: "remote",
      ajaxSorting: true,
    });


    setTimeout(() => {
      document.getElementById("my-tabular-table").appendChild(this.tab);
    })
  }

  id() {
      return this.data[this.schemaConfig.utils.pk_field_name];
  }

  setTableTitle() {
      this.tableTitle = `Liste ${this.schemaConfig.display.undef_labels}`;
  }

  ngOnChanges(changes: SimpleChanges): void {
    this.process();
  }

}

