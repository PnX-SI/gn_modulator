import { Component, OnInit, Input, SimpleChanges, Output, EventEmitter } from "@angular/core";
import { ActivatedRoute, Router, ParamMap } from "@angular/router";
import { ModulesConfigService } from "../../services/config.service"
import { ModulesDataService } from "../../services/data.service"
import { ModulesMapService } from "../../services/map.service"
import { CommonService } from "@geonature_common/service/common.service";
import { ModulesTableService } from "../../services/table.service";
import { ModulesFormService } from "../../services/form.service"
import { ModulesRouteService } from "../../services/route.service"

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
    "base.scss", "base-table.component.scss",
  ],
})
export class BaseTableComponent extends BaseComponent implements OnInit {

  tableID = `table_${Math.random()}`
  _params;
  public table;
  // public height: string = "311px";
  tab = document.createElement("div");

  constructor(
    _route: ActivatedRoute,
    _commonService: CommonService,
    _mapService: ModulesMapService,
    _mConfig: ModulesConfigService,
    _mData: ModulesDataService,
    _mForm: ModulesFormService,
    _router: Router,
    _mTable: ModulesTableService,
    _mRoute: ModulesRouteService,
  ) {
    super(_route, _commonService, _mapService, _mConfig, _mData, _mForm, _router, _mRoute)
    this._name = 'BaseTable';
  }

  ngOnInit() {
  }


  processConfig(): void {
    this.drawTable();
  }

  ajaxRequestFunc = (url, config, paramsTable) => {
    return new Promise((resolve, reject) => {
      const fields = this.columns().map(column => column.field);
      const params = {
        ...paramsTable
      };
      if (!this.displayFilters) {
        params.filters = this.filters;
      }


      const extendedParams = {
        ...params, // depuis tabulator
        fields, // fields
      };
      this._params = extendedParams;
      this._mData.getList(this.schemaName, extendedParams).subscribe((res) => {
        resolve(res);
        if(this.value) {
          setTimeout(() => {this.selectRow(this.value)}, 100);
        }
        return;
      },
      (fail) => {
        reject(fail)
      });

    });
  }

  columns() {
    const columns = this.short
      ? this.schemaConfig.table.columns_short || this.schemaConfig.table.columns
      : this.schemaConfig.table.columns
    ;
    return columns.map(col => {
      const column = utils.copy(col);
      column.headerFilter = column.headerFilter && this.displayFilters;
      return column
    });
  }

  onRowClick = (e, row) => {
    const action = utils.getAttr(e, 'target.attributes.action.nodeValue');
    const event = {
      action: action || 'selected',
      params: {
        value: this.getRowValue(row),
      },
      component: this._name
    }
    this.emitEvent(event)
  };

  getCellValue(cell) {
    const pkFieldName = this.schemaConfig.utils.pk_field_name;
    return cell._cell.row.data[pkFieldName]
  }

  getRowValue(row) {
    const pkFieldName = this.schemaConfig.utils.pk_field_name;
    return row._row.data[pkFieldName]
  }

  onComponentInitialized() {
  }


  /**
   * Definition des colonnes
   *
   * ajout des bouttons voir / éditer (selon les droits ?)
   */
  columnsTable() {

    //column definition in the columns array
    return [
      {
          headerSort: false,
          formatter: (cell, formatterParams, onRendered) => {
            var html = '';
            html += `<span class="table-icon"><i class='fa fa-eye table-icon' action="details"></i></span>`;
            return html;
          },
          width:30,
          hozAlign:"center",
          tooltip: (cell) =>
            `Afficher les détail ${this.schemaConfig.display.prep_label} ${this.getCellValue(cell)}`

          // cellClick: (e, cell) => {
          //   const value = cell._cell.row.data[pkFieldName]
          //   this.onRowSelected.emit({value, action:"detail"})
          // }
        },
        {
          headerSort: false,
          formatter: (cell, formatterParams, onRendered) => {
            var html = '';
            html += `<span class="table-icon"><i class='fa fa-pencil' action="edit"></i></span>`;
            return html;
          },
          width:25,
          hozAlign:"center",
          tooltip: (cell) => `Éditer ${this.schemaConfig.display.def_label} ${this.getCellValue(cell)}`
          // cellClick: (e, cell) => {
          //   const value = cell._cell.row.data[pkFieldName]
          //   this.onRowSelected.emit({value, action:"detail"})
          // }
        },

      // {
      //   formatter:columnIcon('fa fa-eye'),
      //   width:40,
      //   hozAlign:"center",
      //   cellClick: (e, cell) => {
      //     const value = cell._cell.row.data[pkFieldName]
      //     this.onRowSelected.emit({value, action:"detail"})
      //   }
      // },
      // {
      //   formatter:columnIcon('fa fa-pencil'),
      //   width:40,
      //   hozAlign:"center",
      //   cellClick: (e, cell) => {
      //     const value = cell._cell.row.data[pkFieldName]
      //     this.onRowSelected.emit({value, action:"edit"})
      //   }
      // },
      ...this.columns()
      ];
  }

  drawTable(): void {
    this.table = new Tabulator(this.tab, {
      langs: tabulatorLangs,
      locale: 'fr',
      layout: "fitColumns",
      placeholder: "Pas de donnée disponible",
      ajaxFiltering: true,
      height: this.height,
      ajaxRequestFunc: this.ajaxRequestFunc,
      columns: this.columnsTable(),
      ajaxURL: this.schemaConfig.table.url,
      // ajaxURLGenerator: this.ajaxURLGenerator,
      paginationSize: this.size || this.schemaConfig.utils.size,
      pagination: "remote",
      ajaxSorting: true,
      selectable: 1,
      columnMinWidth: 20,
      // tooltips:true,
      rowClick: this.onRowClick
    });

    utils.waitForElement(this.tableID).then((elem) => {
      elem.appendChild(this.tab);
      this.isProcessing=false;
    });

  }

  setComponentTitle() {
      this.componentTitle = `Liste ${this.schemaConfig.display.undef_labels}`;
  }

  processValue(value) {
    if (! value) {
      return;
    }
    if(this.selectRow(value)) {
      return;
    }
    // this.table.setData();
    this._mData.getPageNumber(this.schemaName, value, this._params)
      .subscribe((res) => {
        // set Page
        this.table.setPage(res.page)
      });
  }

  selectRow(value, fieldName=null) {
    if (! fieldName) {
      fieldName = this.pkFieldName();
    }
    const row = this.table.getRows().find(row => row.getData()[fieldName] == value);
    if (!row) {
      return;
    }
    console.log(row)
    this.table.selectRow(row);
    return true;
  }

  ngOnChanges(changes: SimpleChanges) {
    for (const [key, change] of Object.entries(changes)) {
      if(
        ['schemaName', 'filters'].includes(key)
      ) {
        this.process();
      }
      if(key == 'value') {
        // TODO
        this.processValue(this.value)
      }
    }
  }

}

