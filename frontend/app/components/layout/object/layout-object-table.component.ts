import { Component, OnInit, Injector } from "@angular/core";
import { ModulesLayoutObjectComponent } from "./layout-object.component";
import { Observable, of } from "@librairies/rxjs";
import tabulatorLangs from "../../base/table/tabulator-langs";
import Tabulator from "tabulator-tables";
import utils from "../../../utils";

@Component({
  selector: "modules-layout-object-table",
  templateUrl: "layout-object-table.component.html",
  styleUrls: ["../../base/base.scss", "layout-object-table.component.scss"],
})
export class ModulesLayoutObjectTableComponent
  extends ModulesLayoutObjectComponent
  implements OnInit
{
  tableId; // identifiant HTML pour la table;
  counterId; // identifiant HTML pour afficher le counter de données dans le footer;
  table; // object tabulator
  tab = document.createElement("div"); // element
  tableHeight; // hauteur de la table

  _params;

  constructor(_injector: Injector) {
    super(_injector);
    this._name = "layout-object-table";
    this.tableId = `table_${this._id}`;
  }

  drawTable(): void {
    this.table = new Tabulator(this.tab, {
      langs: tabulatorLangs,
      locale: "fr",
      layout: "fitColumns",
      placeholder: "Pas de donnée disponible",
      ajaxFiltering: true,
      height: this.tableHeight || "200px",
      ajaxRequestFunc: this.ajaxRequestFunc,
      columns: this.columnsTable(),
      ajaxURL: this.schemaConfig.table.url,
      paginationSize:
        this.computedLayout.page_size || this.schemaConfig.utils.page_size,
      pagination: "remote",
      headerFilterLiveFilterDelay: 600,
      ajaxSorting: true,
      initialSort: utils.copy(this.schemaConfig.table.sort) || [],
      // {column:this.pkFieldName(), dir:"asc"}, //sort by this first
      selectable: 1,
      columnMinWidth: 20,
      footerElement: `<span class="counter" id=counter></span>`,
      // tooltips:true,
      rowClick: this.onRowClick,
    });

    utils.waitForElement(this.tableId).then((elem) => {
      elem.appendChild(this.tab);
      this.isProcessing = false;
    });
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
          var html = "";
          html += `<span class="table-icon"><i class='fa fa-eye table-icon' action="details"></i></span>`;
          return html;
        },
        width: 30,
        hozAlign: "center",
        tooltip: (cell) =>
          `Afficher les détail ${
            this.schemaConfig.display.du_label
          } ${this.getCellValue(cell)}`,
      },
      {
        headerSort: false,
        formatter: (cell, formatterParams, onRendered) => {
          const editAllowed =
            cell._cell.row.data["cruved_ownership"] <=
            this.moduleConfig.module.cruved["U"];
          var html = "";
          html += `<span class="table-icon ${
            editAllowed ? "" : "disabled"
          }"><i class='fa fa-pencil' ${
            editAllowed ? 'action="edit"' : ""
          }></i></span>`;
          return html;
        },
        width: 25,
        hozAlign: "center",
        tooltip: (cell) => {
          const editAllowed =
            cell._cell.row.data["cruved_ownership"] <=
            this.moduleConfig.module.cruved["U"];
          return editAllowed
            ? `Éditer ${this.schemaConfig.display.le_label} ${this.getCellValue(
                cell
              )}`
            : "";
        },
      },
      ...this.columns(),
    ];
  }

  columns() {
    const columns = this.computedLayout.short
      ? this.schemaConfig.table.columns_short || this.schemaConfig.table.columns
      : this.schemaConfig.table.columns;
    return columns.map((col) => {
      const column = utils.copy(col);
      column.headerFilter =
        column.headerFilter && this.computedLayout.display_filters;
      return column;
    });
  }

  onRowClick = (e, row) => {
    const action =
      utils.getAttr(e, "target.attributes.action.nodeValue") || "selected";
    const value = this.getRowValue(row);

    if (["details", "edit"].includes(action)) {
      this._mPage.processAction(action, this.objectName(), {
        value,
      });

    }

    if (action == "selected") {
      this._mObject.setObjectValue(this.objectName(), "value", value);
    }
  };

  getCellValue(cell) {
    const pkFieldName = this.schemaConfig.utils.pk_field_name;
    return cell._cell.row.data[pkFieldName];
  }

  getRowValue(row) {
    const pkFieldName = this.schemaConfig.utils.pk_field_name;
    return row._row.data[pkFieldName];
  }

  ajaxRequestFunc = (url, config, paramsTable) => {
    return new Promise((resolve, reject) => {
      const fields = this.columns().map((column) => column.field);

      fields.push("cruved_ownership");

      if (!fields.includes(this.schemaConfig.utils.pk_field_name)) {
        fields.push(this.schemaConfig.utils.pk_field_name);
      }
      const params = {
        ...paramsTable,
        page_size: paramsTable.size,
      };
      if (!this.computedLayout.display_filters) {
        params.filters = this.getObjectFilters();
      }

      // prefiltres
      const prefilters = this.getObjectPreFilters();

      if(prefilters) {
        params.prefilters = prefilters;
      }

      const extendedParams = {
        ...params, // depuis tabulator
        fields, // fields
      };
      this._params = extendedParams;
      this._mData
        .getList(this.schemaName(), extendedParams)
        .subscribe(
          (res) => {
            // process lists

            for (const column of this.columns()) {
              for (const d of res.data) {
                if (column["field"].includes(".")) {
                  let val = utils.getAttr(d, column["field"]);
                  val = Array.isArray(val) ? val.join(", ") : val;
                  delete d[column["field"].split(".")[0]];
                  utils.setAttr(d, column["field"], val);
                }
              }
            }

            resolve(res);
            utils
              .waitForElement(
                "counter",
                document.querySelector(`#${this.tableId}`)
              )
              .then((counterElement) => {

                (counterElement as any).innerHTML = `Nombre de données filtrées / total : <b>${res.filtered} /  ${res.total}</b>`;
              });

            if (this.getObjectValue()) {
              setTimeout(() => {
                this.selectRow(
                  this.getObjectValue(  )
                );
              }, 100);
            }
            return;
          },
          (fail) => {
            reject(fail);
          }
        );
    });
  };

  processValue(value) {
    if (!value) {
      return;
    }
    if (this.selectRow(value)) {
      return;
    }

    // TODO une seule requete pour les getPageNumber et setPage ??
    this._mData
      .getPageNumber(this.schemaName(), value, this._params)
      .subscribe((res) => {
        // set Page
        this.table.setPage(res.page);
      });
  }

  selectRow(value, fieldName = null) {
    //
    if(!value) {
      return;
    }
    this.log(value)

    this.table.deselectRow();
    if (!fieldName) {
      fieldName = this.pkFieldName();
    }
    const row = this.table
      .getRows()
      .find((row) => row.getData()[fieldName] == value);

    if (row) {
      this.table.selectRow(row);
    }

    return !!row;
  }

  processConfig() {
    this.drawTable();
  }

  onHeightChange() {
    if (!this.table) {
      return;
    }
    this.table.setHeight("50px");

    const elem = document.getElementById(this._id);
    if (!elem) {
      return;
    }
    this.tableHeight = `${elem.clientHeight}px`;
    this.table.setHeight(this.tableHeight);
  }


  processData(data) {
    console.log('process table data')
  }

  processFilters(filters: any): void {
    console.log('process table filter')

  }

  processPreFilters(filters: any): void {
    console.log('process table prefilter')
  }


  getData(): Observable<any> {
    return of(true);
  }
}
