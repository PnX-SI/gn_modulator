import { Component, OnInit, Input, SimpleChanges, Output, EventEmitter } from "@angular/core";
import { ActivatedRoute, Router, ParamMap } from "@angular/router";
import { ModulesConfigService } from "../../services/config.service"
import { ModulesDataService } from "../../services/data.service"
import { ModulesMapService } from "../../services/map.service"
import { CommonService } from "@geonature_common/service/common.service";

import { mergeMap, concatMap } from "@librairies/rxjs/operators";
import { Observable, of, forkJoin } from "@librairies/rxjs";
import tabulatorLangs  from './table/tabulator-langs'
import Tabulator from "tabulator-tables";
import utils from "../../utils"
import { BaseComponent } from "./base.component";

@Component({
  selector: "modules-base-table",
  templateUrl: "base-table.component.html",
  styleUrls: [
    "../../../node_modules/tabulator-tables/dist/css/tabulator_site.min.css", //patch pour ne pas passer par angular.json
    "base-table.component.scss",
  ],
})
export class BaseTableComponent extends BaseComponent implements OnInit {

  @Output() onRowSelected: EventEmitter<any> = new EventEmitter<any>();

  tableInitialized = false;
  tableTitle = null;

  public table;
  public height: string = "311px";
  tab = document.createElement("div");

  constructor(
    _route: ActivatedRoute,
    _commonService: CommonService,
    _mapService: ModulesMapService,
    _mConfig: ModulesConfigService,
    _mData: ModulesDataService,
    _router: Router,
  ) {
    super(_route, _commonService, _mapService, _mConfig, _mData, _router)
    this._name = 'BaseTable';
  }

  ngOnInit() {
    // load_config
    this.process();
  }

  process() {
    if(this.isProcessing) {
      return
    }
    this.isProcessing = true;
    // load_config
    this._mConfig.loadConfig(this.schemaName)
      .subscribe((schemaConfig) => {
          this.componentInitialized = false;
          this.schemaConfig = schemaConfig;
          this.setTableTitle();
          this.componentInitialized = true;
          this.drawTable();
      });
  }



  ajaxRequestFunc = (url, config, params) => {
    return new Promise((resolve, reject) => {
      const fields = this.schemaConfig.table.columns.map(column => column.field);
      const extendedParams = {
        ...params, // depuis tabulator
        fields, // fields
      };
      this._mData.getList(this.schemaName, extendedParams).subscribe((res) => {
        resolve(res);
        return;
      },
      (fail) => {
        reject(fail)
      });

    });
  }

  /**
   * Definition des colonnes
   *
   * ajout des bouttons voir / éditer (selon les droits ?)
   */
  columns() {
    var columnIcon = (icon) => function(cell, formatterParams, onRendered){ //plain text value
      return `<i class='${icon}'></i>`;
    };

    const pkFieldName = this.schemaConfig.utils.pk_field_name;

    //column definition in the columns array
    return [
      {
        formatter:columnIcon('fa fa-eye'),
        width:40,
        hozAlign:"center",
        cellClick: (e, cell) => {
          const value = cell._cell.row.data[pkFieldName]
          this.onRowSelected.emit({value, action:"detail"})
        }
      },
      {
        formatter:columnIcon('fa fa-pencil'),
        width:40,
        hozAlign:"center",
        cellClick: (e, cell) => {
          const value = cell._cell.row.data[pkFieldName]
          this.onRowSelected.emit({value, action:"edit"})
        }
      },
      ...this.schemaConfig.table.columns
      ];
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
      layout: "fitColumns",
      placeholder: "No Data Set",
      ajaxFiltering: true,
      ajaxRequestFunc: this.ajaxRequestFunc,
      columns: this.columns(),
      ajaxURL: this.schemaConfig.table.url,
      // ajaxURLGenerator: this.ajaxURLGenerator,
      paginationSize: this.schemaConfig.utils.size,
      pagination: "remote",
      ajaxSorting: true,
    });

    utils.waitForElement("my-tabular-table").then((elem) => {
      elem.appendChild(this.tab);
      this.isProcessing=false;
    });

  }

  id() {
      return this.data[this.schemaConfig.utils.pk_field_name];
  }

  setTableTitle() {
      this.tableTitle = `Liste ${this.schemaConfig.display.undef_labels}`;
  }

  ngOnChanges(changes: SimpleChanges): void {
    for (const [key, change] of Object.entries(changes)) {
      if(
        ['schemaName'].includes(key)
      ) {
        this.process();
      }
      if(key == 'value') {
        // TODO
      }
    }
  }

}

