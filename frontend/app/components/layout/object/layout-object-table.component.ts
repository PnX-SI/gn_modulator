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

  firstDraw;
  _params;
  modalDeleteLayout;

  constructor(_injector: Injector) {
    super(_injector);
    this._name = "layout-object-table";
    this.tableId = `table_${this._id}`;
  }

  postInit() {}

  onRedrawElem(): void {
    const elem = document.getElementById(this._id);
    this.onHeightChange(true);
    this.setCount();
  }

  drawTable(): void {
    const sortTable = this.objectConfig.table.sort
      ? this.objectConfig.table.sort.split(",").map((sort) => {
          let column = sort,
            dir = "asc";
          if (sort[sort.length - 1] == "-") {
            column = sort.substring(0, sort.length - 1);
            dir = "desc";
          }
          return { column, dir };
        })
      : [];

    this.table = new Tabulator(this.tab, {
      langs: tabulatorLangs,
      locale: "fr",
      layout: "fitColumns",
      placeholder: "Pas de donnée disponible",
      ajaxFiltering: true,
      height: this.tableHeight || "200px",
      ajaxRequestFunc: this.ajaxRequestFunc,
      columns: this.columnsTable(),
      ajaxURL: this.objectConfig.table.url,
      paginationSize:
        this.computedLayout.page_size || this.objectConfig.utils.page_size,
      pagination: "remote",
      headerFilterLiveFilterDelay: 600,
      ajaxSorting: true,
      initialSort: sortTable,
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
          html += `<span class="table-icon" action="details"><i class='fa fa-eye table-icon action' action="details"></i></span>`;
          return html;
        },
        width: 30,
        hozAlign: "center",
        tooltip: (cell) =>
          `Afficher les détail ${
            this.objectConfig.display.du_label
          } ${this.getCellValue(cell)}`,
      },
      {
        headerSort: false,
        formatter: (cell, formatterParams, onRendered) => {
          const editAllowed =
            cell._cell.row.data["ownership"] <=
            this._mPage.moduleConfig.cruved["U"];
          var html = "";
          html += `<span class="table-icon ${
            editAllowed ? "" : "disabled"
          }"><i class='fa fa-pencil action' ${
            editAllowed ? 'action="edit"' : ""
          }></i></span>`;
          return html;
        },
        width: 25,
        hozAlign: "center",
        tooltip: (cell) => {
          const editAllowed =
            cell._cell.row.data["ownership"] <=
            this._mPage.moduleConfig.cruved["U"];
          return editAllowed
            ? `Éditer ${this.objectConfig.display.le_label} ${this.getCellValue(
                cell
              )}`
            : "";
        },
      },
      {
        headerSort: false,
        formatter: (cell, formatterParams, onRendered) => {
          const deleteAllowed =
            cell._cell.row.data["ownership"] <=
            this._mPage.moduleConfig.cruved["D"];
          var html = "";
          html += `<span class="table-icon ${
            deleteAllowed ? "" : "disabled"
          }"><i class='fa fa-trash action' ${
            deleteAllowed ? 'action="delete"' : ""
          }></i></span>`;
          return html;
        },
        width: 25,
        hozAlign: "center",
        tooltip: (cell) => {
          const deleteAllowed =
            cell._cell.row.data["ownership"] <=
            this._mPage.moduleConfig.cruved["D"];
          return deleteAllowed
            ? `Supprimer ${
                this.objectConfig.display.le_label
              } ${this.getCellValue(cell)}`
            : "";
        },
      },
      ...this.columns(),
    ];
  }

  columns() {
    const columns = this.objectConfig.table.columns;
    return columns.map((col) => {
      const column = utils.copy(col);
      column.headerFilter =
        column.headerFilter && this.computedLayout.display_filters;
      // pour les dates
      column.formatter = (cell, formatterParams, onRendered) => {
        if (col.type == "date") {
          // pour avoir les dates en français
          let cellData = cell._cell.row.data[col.field];
          return cellData && cellData.split("-").reverse().join("/");
        }
        if (col.field.includes(".")) {
          return utils.getAttr(cell._cell.row.data, col.field);
        }
        return cell._cell.row.data[col.field];
      };

      return column;
    });
  }

  onRowClick = (e, row) => {
    let action = utils.getAttr(e, "target.attributes.action.nodeValue")
      ? utils.getAttr(e, "target.attributes.action.nodeValue")
      : e.target.getElementsByClassName("action").length
      ? utils.getAttr(
          e.target.getElementsByClassName("action")[0],
          "attributes.action.nodeValue"
        )
      : "selected";
    const value = this.getRowValue(row);

    if (["details", "edit"].includes(action)) {
      this._mPage.processAction({
        action,
        objectName: this.objectName(),
        value,
      });
    }

    if (action == "delete") {
      this._mLayout.openModal(
        this.modalDeleteLayout.modal_name,
        this.getRowData(row)
      );
    }

    if (action == "selected") {
      this.setObject({ value });
    }
  };

  getCellValue(cell) {
    const pkFieldName = this.objectConfig.utils.pk_field_name;
    return cell._cell.row.data[pkFieldName];
  }

  getRowValue(row) {
    const pkFieldName = this.objectConfig.utils.pk_field_name;
    return this.getRowData(row)[pkFieldName];
  }

  getRowData(row) {
    return row._row.data;
  }

  ajaxRequestFunc = (url, config, paramsTable) => {
    return new Promise((resolve, reject) => {
      const fields = this.columns().map((column) => column.field);

      fields.push("ownership");

      if (!fields.includes(this.objectConfig.utils.pk_field_name)) {
        fields.push(this.objectConfig.utils.pk_field_name);
      }
      const params = {
        ...paramsTable,
        page_size: paramsTable.size,
        sort: paramsTable.sorters
          .filter((s) => s.field)
          .map((s) => `${s.field}${s.dir == "desc" ? "-" : ""}`)
          .join(","),
      };
      if (!this.computedLayout.display_filters) {
        params.filters = this.getDataFilters();
      }

      // prefiltres
      const prefilters = this.getDataPreFilters();

      if (prefilters) {
        params.prefilters = prefilters;
      }

      const extendedParams = {
        ...params, // depuis tabulator
        fields, // fields
      };
      this._params = extendedParams;
      delete extendedParams["sorters"];
      console.log(extendedParams);
      this._mData
        .getList(this.moduleCode(), this.objectName(), extendedParams)
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
            this.onHeightChange(true);

            if (this.getDataValue()) {
              setTimeout(() => {
                this.selectRow(this.getDataValue());
              }, 100);
            }

            //
            this.processTotalFiltered(res);
            this.setCount();

            return;
          },
          (fail) => {
            reject(fail);
          }
        );
    });
  };

  setCount() {
    utils
      .waitForElement("counter", document.querySelector(`#${this.tableId}`))
      .then(
        (counterElement) => {
          // (counterElement as any).innerHTML = `Nombre de données filtrées / total : <b>${res.filtered} /  ${res.total}</b>`;
          (
            counterElement as any
          ).innerHTML = `<b>${this.data.filtered} /  ${this.data.total}</b>`;
        },
        (error) => {
          console.error("waitForElement erreur");
        }
      );
  }

  processValue(value) {
    if (!value) {
      return;
    }

    if (this.selectRow(value)) {
      // return;
    }

    // TODO une seule requete pour les getPageNumber et setPage ??
    this._mData
      .getPageNumber(this.moduleCode(), this.objectName(), value, this._params)
      .subscribe((res) => {
        // set Page
        this.table.setPage(res.page);
      });
  }

  selectRow(value, fieldName = null) {
    //
    if (!value) {
      return;
    }

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
    this.modalDeleteLayout = this._mSchema.modalDeleteLayout(
      this.objectConfig,
      `delete_modal_${this._id}`
    );
    this.drawTable();
  }

  processFilters() {
    this.drawTable();
  }

  onHeightChange(force = false) {
    if (!this.table) {
      return;
    }
    const docHeight = document.body.clientHeight;

    // si la taille du body n'a pas changé on retourne
    if (this.docHeightSave == docHeight && !force) {
      return;
    }

    if (this.docHeightSave > docHeight || !this.docHeightSave) {
      this.table.setHeight("50px");
    }

    this.docHeightSave = docHeight;

    setTimeout(() => {
      const elem = document.getElementById(this._id);
      if (!elem) {
        return;
      }
      this.tableHeight = `${elem.clientHeight}px`;
      this.table.setHeight(this.tableHeight);
    }, 10);
  }

  getData(): Observable<any> {
    return of(true);
  }

  refreshData(objectName: any): void {
    if (objectName == this.data.object_name) {
      this.drawTable();
    }
  }
}
