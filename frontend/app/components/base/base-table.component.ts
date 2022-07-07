import { Component, OnInit, SimpleChanges } from "@angular/core";
import { ActivatedRoute, Router } from "@angular/router";

import { ModulesService } from "../../services/all.service";

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
    _services: ModulesService
  ) {
    super(_services)
    this._name = 'BaseTable';
  }

  ngOnInit() {
    this.initHeight();
  }

  afterResize(): void {
    this.drawTable();
  }

  processConfig(): void {
    this.drawTable();
  }

  ajaxRequestFunc = (url, config, paramsTable) => {
    return new Promise((resolve, reject) => {
      const fields = this.columns().map(column => column.field);

      fields.push('cruved_ownership');

      if(!fields.includes(this.schemaConfig.utils.pk_field_name)){
        fields.push(this.schemaConfig.utils.pk_field_name)
      }
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
      this._services.mData.getList(this.schemaName, extendedParams).subscribe((res) => {

        // process lists

        for (const column of this.columns()) {
          for (const d of res.data) {
            if( column['field'].includes('.')) {
              let val = utils.getAttr(d, column['field'])
              val = Array.isArray(val) ? val.join(', ') : val;
              delete d[column['field'].split('.')[0]]
              utils.setAttr(d,  column['field'], val);
            }
          }
        }

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
            `Afficher les détail ${this.schemaConfig.display.du_label} ${this.getCellValue(cell)}`

        },
        {
          headerSort: false,
          formatter: (cell, formatterParams, onRendered) => {
            const editAllowed = cell._cell.row.data['cruved_ownership'] <= this.moduleConfig.module.cruved['U'];
            var html = '';
            html += `<span class="table-icon ${editAllowed ? '' : 'disabled'}"><i class='fa fa-pencil' ${editAllowed ? 'action="edit"': ''}></i></span>`;
            return html;
          },
          width:25,
          hozAlign:"center",
          tooltip: (cell) => {
            const editAllowed = cell._cell.row.data['cruved_ownership'] <= this.moduleConfig.module.cruved['U'];
            return editAllowed
              ? `Éditer ${this.schemaConfig.display.le_label} ${this.getCellValue(cell)}`
              : ''
          }
        },

      // {
      //   formatter:columnIcon('fa fa-eye'),
      //   width:40,
      //   hozAlign:"center",
      //   cellClick: (e, cell) => {
      //     const value = cell._cell.row.data[pkFieldName]
      //     this.onRowSelected.emit({value, action:"details"})
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
    console.log(this.schemaConfig.table.sort)
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
      initialSort:utils.copy(this.schemaConfig.table.sort) || [],
      // {column:this.pkFieldName(), dir:"asc"}, //sort by this first
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
      this.componentTitle = `Liste ${this.schemaConfig.display.des_labels}`;
  }

  processValue(value) {
    if (! value) {
      return;
    }
    if(this.selectRow(value)) {
      return;
    }
    // this.table.setData();
    this._services.mData.getPageNumber(this.schemaName, value, this._params)
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
      if(key == 'height') {
        // TODO
        this.drawTable()
      }

    }
  }

}

