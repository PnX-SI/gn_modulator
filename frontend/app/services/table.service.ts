import { Injectable } from '@angular/core';
import utils from '../utils';

@Injectable()
export class ModulesTableService {
  constructor() {}

  getSorters(objectConfig) {
    const sortTable = objectConfig?.table.sort
      ? objectConfig?.table.sort.split(',').map((sort) => {
          let column = sort,
            dir = 'asc';
          if (sort[sort.length - 1] == '-') {
            column = sort.substring(0, sort.length - 1);
            dir = 'desc';
          }
          return { column, dir };
        })
      : [];
    return sortTable;
  }

  getCellValue(cell, objectConfig) {
    const pkFieldName = objectConfig.utils.pk_field_name;
    return cell._cell.row.data[pkFieldName];
  }

  /**
   * Definition des colonnes
   *
   * ajout des bouttons voir / éditer (selon les droits ?)
   */
  columnsTable(layout, objectConfig, moduleConfig) {
    //column definition in the columns array
    return [
      {
        headerSort: false,
        formatter: (cell, formatterParams, onRendered) => {
          var html = '';
          html += `<span class="table-icon" action="details"><i class='fa fa-eye table-icon action' action="details"></i></span>`;
          return html;
        },
        width: 30,
        hozAlign: 'center',
        tooltip: (cell) =>
          `Afficher les détail ${objectConfig.display.du_label} ${this.getCellValue(
            cell,
            objectConfig
          )}`,
      },
      {
        headerSort: false,
        formatter: (cell, formatterParams, onRendered) => {
          const editAllowed = cell._cell.row.data['ownership'] <= moduleConfig.cruved['U'];
          var html = '';
          html += `<span class="table-icon ${
            editAllowed ? '' : 'disabled'
          }"><i class='fa fa-pencil action' ${editAllowed ? 'action="edit"' : ''}></i></span>`;
          return html;
        },
        width: 25,
        hozAlign: 'center',
        tooltip: (cell) => {
          const editAllowed = cell._cell.row.data['ownership'] <= moduleConfig.cruved['U'];
          return editAllowed
            ? `Éditer ${objectConfig.display.le_label} ${this.getCellValue(cell, objectConfig)}`
            : '';
        },
      },
      {
        headerSort: false,
        formatter: (cell, formatterParams, onRendered) => {
          const deleteAllowed = cell._cell.row.data['ownership'] <= moduleConfig.cruved['D'];
          var html = '';
          html += `<span class="table-icon ${
            deleteAllowed ? '' : 'disabled'
          }"><i class='fa fa-trash action' ${deleteAllowed ? 'action="delete"' : ''}></i></span>`;
          return html;
        },
        width: 25,
        hozAlign: 'center',
        tooltip: (cell) => {
          const deleteAllowed = cell._cell.row.data['ownership'] <= moduleConfig.cruved['D'];
          return deleteAllowed
            ? `Supprimer ${objectConfig.display.le_label} ${this.getCellValue(cell, objectConfig)}`
            : '';
        },
      },
      ...this.columns(layout, objectConfig),
    ];
  }

  columns(layout, objectConfig) {
    const columns = objectConfig.table.columns;
    return columns.map((col) => {
      const column = utils.copy(col);
      column.headerFilter = column.headerFilter && layout.display_filters;
      // pour les dates
      column.formatter = (cell, formatterParams, onRendered) => {
        if (col.type == 'date') {
          // pour avoir les dates en français
          let cellData = cell._cell.row.data[col.field];
          return cellData && cellData.split('-').reverse().join('/');
        }
        if (col.field.includes('.')) {
          return utils.getAttr(cell._cell.row.data, col.field);
        }
        return cell._cell.row.data[col.field];
      };
      delete column.type;
      return column;
    });
  }
}
