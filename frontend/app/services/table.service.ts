import { Injectable, Injector } from '@angular/core';
import utils from '../utils';
import { ModulesConfigService } from './config.service';
import { ModulesObjectService } from './object.service';
import { ModulesActionService } from './action.service';
import { ModulesRouteService } from './route.service';
import { ModulesLayoutService } from './layout.service';
@Injectable()
export class ModulesTableService {
  _mAction: ModulesActionService;
  _mConfig: ModulesConfigService;
  _mObject: ModulesObjectService;
  _mRoute: ModulesRouteService;
  _mLayout: ModulesLayoutService;

  constructor(private _injector: Injector) {
    this._mConfig = this._injector.get(ModulesConfigService);
    this._mObject = this._injector.get(ModulesObjectService);
    this._mAction = this._injector.get(ModulesActionService);
    this._mRoute = this._injector.get(ModulesRouteService);
    this._mLayout = this._injector.get(ModulesLayoutService);
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
   *  - L'appartenance (scope) sera fournie par les données du rang de la cellule dans les fonction formatter et tooltip)
   * */
  columnAction(layout, context, action) {
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

    const { actionAllowed, actionMsg } = this._mObject.checkAction(context, action);

    if (actionAllowed == null && !(layout?.actions && layout?.actions[action])) {
      return;
    }

    return {
      headerSort: false,
      formatter: (cell, formatterParams, onRendered) => {
        const scope = cell._cell.row.data['scope'];
        let { actionAllowed, actionMsg } = this._mObject.checkAction(context, action, scope);
        actionAllowed = actionAllowed || !!layout?.actions?.[action];
        const html = `<span class="table-icon ${actionAllowed ? '' : 'disabled'}"><i class='fa ${
          iconAction[action]
        }'></i></span>`;
        return html;
      },
      width: 22,
      hozAlign: 'center',
      cellClick: (e, cell) => {
        const data = cell._cell.row.data;
        const value = this._mObject.objectId({ context, data });
        if (layout?.actions?.[action]) {
          const href = layout.actions[action].url.replace('<id>', value);
          this._mRoute.redirect(href);
          return;
        }

        if (['R', 'U'].includes(action)) {
          this._mAction.processAction({
            action: actionTxt[action],
            context,
            value,
          });
        }

        if (action == 'D') {
          this._mLayout.openModal('delete', data);
        }
      },
      tooltip: (cell) => {
        if (layout.actions?.[action]) {
          return layout?.actions[action].title;
        }
        const scope = cell._cell.row.data['scope'];
        const { actionAllowed, actionMsg } = this._mObject.checkAction(context, action, scope);
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
  columnsAction(layout, context) {
    const columnsAction = 'RUD'
      .split('')
      .map((action) => this.columnAction(layout, context, action))
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
    return [...this.columnsAction(layout, context), ...this.columns(fields, layout, context)];
  }

  columnLayoutItem(layoutItem, context) {
    let layoutItemOut = {};

    if (typeof layoutItem == 'string') {
      layoutItemOut['key'] = layoutItemOut['field'] = layoutItem;
    } else {
      layoutItemOut = utils.copy(layoutItem);
    }

    const property = this._mObject.property(context, layoutItem.key);
    layoutItemOut['title'] =
      layoutItem['title'] || layoutItem.includes('.') ? property.parent?.title : property.title;
    layoutItemOut['type'] = layoutItem['type'] || property.type;
    layoutItemOut['field'] = layoutItem['key'];

    if (layoutItemOut['hidden']) {
      layoutItemOut['visible'] = false;
    }

    if (layoutItemOut['headerFilter'] == null) {
      layoutItemOut['headerFilter'] == true;
    }

    return layoutItemOut;
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
