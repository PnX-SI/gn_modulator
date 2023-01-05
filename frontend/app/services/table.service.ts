import { Injectable, Injector } from '@angular/core';
import utils from '../utils';
import { ModulesPageService } from './page.service';
import { ModulesConfigService } from './config.service';
import { ModulesObjectService } from './object.service';
@Injectable()
export class ModulesTableService {
  _mPage: ModulesPageService;
  _mConfig: ModulesConfigService;
  _mObject: ModulesObjectService;

  constructor(private _injector: Injector) {
    this._mPage = this._injector.get(ModulesPageService);
    this._mConfig = this._injector.get(ModulesConfigService);
    this._mObject = this._injector.get(ModulesObjectService);
  }

  /** permet de passer des paramètre de tri du format tabulator
   *   au format de l'api de liste
   * [{column: 'field1', dir: 'asc'},{column: 'field2', dir: 'desc'}] -> 'field1,field2-'
   *
   */
  processTableSorters(tableSort) {
    return tableSort
      .filter((s) => s.field)
      .map((s) => `${s.field}${s.dir == 'desc' ? '-' : ''}`)
      .join(',');
  }

  /** permet de traiter la definition de sort d'un object
   * pour le passer au format tabulator
   *   'field1,field2-' -> [{column: 'field1', dir: 'asc'},{column: 'field2', dir: 'desc'}]
   */
  processObjectSorters(sort) {
    const sortTable = sort
      ? sort.split(',').map((sort) => {
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
   * columnAction
   *   - Renvoie la définition de la colonne pour les actions:
   *    voir, éditer, supprimer
   *  - On utilise mPage.chekcLink pour voir si et comment on affiche l'action en question
   *  - L'appartenance (ownership) sera fournie par les données du rang de la cellule dans les fonction formatter et tooltip)
   * */
  columnAction(context, action) {
    // test si l'action est possible (ou avant)

    const iconAction = {
      R: 'fa-eye',
      U: 'fa-edit',
      D: 'fa-trash',
    };

    const actionTxt = {
      R: 'details',
      U: 'edit',
      D: 'delete',
    };

    const { actionAllowed, actionMsg } = this._mPage.checkAction(context, action);
    if (actionAllowed == null) {
      return;
    }

    return {
      headerSort: false,
      formatter: (cell, formatterParams, onRendered) => {
        const ownership = cell._cell.row.data['ownership'];
        const { actionAllowed, actionMsg } = this._mPage.checkAction(context, action, ownership);
        return `<span class="table-icon ${actionAllowed ? '' : 'disabled'}"><i class='fa ${
          iconAction[action]
        } action' ${actionAllowed ? 'action="' + actionTxt[action] + '"' : ''}></i></span>`;
      },
      width: 22,
      hozAlign: 'center',
      tooltip: (cell) => {
        const ownership = cell._cell.row.data['ownership'];
        const { actionAllowed, actionMsg } = this._mPage.checkAction(context, action, ownership);
        return actionMsg;
      },
    };
  }

  /** columnsAction
   *
   * on traite toutes les colonnes d'action pour les action
   * R: read / details
   * U: update / edit
   * D: delete
   */
  columnsAction(context) {
    const columnsAction = 'RUD'
      .split('')
      .map((action) => this.columnAction(context, action))
      .filter((columnAction) => !!columnAction);
    return columnsAction;
  }

  /**
   * Definition des colonnes
   *
   * ajout des bouttons voir / éditer (selon les droits ?)
   */
  columnsTable(fields, layout, context) {
    //column definition in the columns array
    return [...this.columnsAction(context), ...this.columns(fields, layout, context)];
  }

  columnLayoutItem(layoutItem, context) {
    if (typeof layoutItem == 'string') {
      const property = this._mObject.property(context, layoutItem);
      let title = layoutItem.includes('.') ? property.parent.title : property.title;
      return {
        field: layoutItem,
        title,
        headerFilter: true,
        type: property.type,
      };
    }

    // TODO complétenter avec la property ???
    return layoutItem;
  }

  columns(fields, layout, context) {
    const columns = fields.map((item) => this.columnLayoutItem(item, context));

    return columns.map((col) => {
      const column = utils.copy(col);
      column.headerFilter = column.headerFilter && layout.display_filters;
      // pour les dates
      column.formatter = (cell, formatterParams, onRendered) => {
        let value = cell._cell.row.data[column.field];

        if (col.type == 'date' && !!value) {
          // pour avoir les dates en français
          return value.split('-').reverse().join('/');
        }

        return value;
      };
      delete column.type;
      return column;
    });
  }
}
