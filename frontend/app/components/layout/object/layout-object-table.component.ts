import { Component, OnInit, Injector, ViewEncapsulation } from '@angular/core';
import { ModulesLayoutObjectComponent } from './layout-object.component';
import { Observable, of } from '@librairies/rxjs';
import { ModulesTableService } from '../../../services/table.service';
import { ModulesActionService } from '../../../services/action.service';
import tabulatorLangs from '../../base/table/tabulator-langs';
import Tabulator from 'tabulator-tables';
import utils from '../../../utils';

@Component({
  selector: 'modules-layout-object-table',
  templateUrl: 'layout-object-table.component.html',
  styleUrls: ['../../base/base.scss', './layout-object-table.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class ModulesLayoutObjectTableComponent
  extends ModulesLayoutObjectComponent
  implements OnInit
{
  tableId; // identifiant HTML pour la table;
  counterId; // identifiant HTML pour afficher le counter de données dans le footer;
  table; // object tabulator
  tab = document.createElement('div'); // element
  tableHeight; // hauteur de la table

  initCount;

  pageSize;
  apiParams;
  modalDeleteLayout = {
    code: 'utils.modal_delete',
  };
  _mTable: ModulesTableService;
  _mAction: ModulesActionService;

  // données récupérées par un appel à getPage
  pageData: any;

  constructor(_injector: Injector) {
    super(_injector);
    this._name = 'layout-object-table';
    this._mTable = this._injector.get(ModulesTableService);
    this._mAction = this._injector.get(ModulesActionService);
    this.tableId = `table_${this._id}`;
    this.bCheckParentsHeight = true;
  }

  onRedrawElem(): void {
    this.reDrawTable();
  }

  columns() {
    return this._mTable.columnsTable(this.computedItems, this.computedLayout, this.context);
  }

  drawTable(): void {
    this.pageSize = this.pageSize || this.computedLayout.page_size || 10;
    this.table = new Tabulator(this.tab, {
      langs: tabulatorLangs,
      locale: 'fr',
      layout: 'fitColumns',
      placeholder: 'Pas de donnée disponible',
      ajaxFiltering: true,
      height: this.tableHeight || '200px',
      ajaxRequestFunc: this.ajaxRequestFunc,
      columns: this.columns(),
      ajaxURL: this._mConfig.objectUrl(this.context.module_code, this.context.object_code),
      paginationSize: this.pageSize,
      pagination: 'remote',
      headerFilterLiveFilterDelay: 600,
      ajaxSorting: true,
      initialSort: this._mTable.processObjectSorters(this.computedLayout.sort),
      selectable: 1,
      columnMinWidth: 20,
      footerElement: `<span class="counter" id=counter></span>`,
      // tooltips:true,
      rowClick: this.onRowClick,
    });

    utils.waitForElement(this.tableId).then((elem: any) => {
      elem.appendChild(this.tab);
      this.isProcessing = false;
    });
  }

  onRowClick = (e, row) => {
    const value = this.getRowValue(row);
    this.setObject({ value });
  };

  getRowValue(row) {
    const pkFieldName = this.pkFieldName();
    return this.getRowData(row)[pkFieldName];
  }

  getRowData(row) {
    return row._row.data;
  }

  /** ajaxRequestFunc
   *
   * la promesse qui va être appelée par le composant tabulator
   * - on se sert de la fonction getList du service _mData
   * - on gère les paramètre de route
   *  - page_size, page, filters, prefilters, sort
   *
   */
  ajaxRequestFunc = (url, config, paramsTable) => {
    return new Promise((resolve, reject) => {
      // calcul des paramètres
      // TODO traiter les paramètres venant des filtres de la table
      const params = {
        ...paramsTable,
        page_size: paramsTable.size,
        sort: this._mTable.processTableSorters(paramsTable.sorters),
      };

      delete params['sorters'];

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
        fields: this.fields({ addDefault: true }), // fields
        flat_keys: true, // sortie à plat
      };

      // on garde les paramètres en mémoire pour les utiliser dans getPageNumber();
      this.apiParams = utils.copy(extendedParams);
      // pour ne pas trainer sortersça dans l'api
      delete extendedParams['sorters'];

      // patch
      if (extendedParams.prefilters?.includes('undefined')) {
        console.error('prefilter inconnu');
        return of({});
      }

      const observable = this.pageData
        ? of(this.pageData)
        : this._mData.getList(this.moduleCode(), this.objectCode(), this.apiParams);

      observable.subscribe(
        (res) => {
          if (this.pageData) {
            this.pageData = null;
          }
          resolve(res);
          this.reDrawTable();

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
        },
      );
    });
  };

  setCount() {
    utils.waitForElement('counter', document.querySelector(`#${this.tableId}`)).then(
      (counterElement) => {
        this.initCount = true;
        // (counterElement as any).innerHTML = `Nombre de données filtrées / total : <b>${res.filtered} /  ${res.total}</b>`;
        (counterElement as any).innerHTML = `<b>${this.context.nb_filtered || 0} /  ${
          this.context.nb_total || 0
        }</b>`;
      },
      (error) => {},
    );
  }

  processValue(value) {
    if (!value) {
      return;
    }

    if (!this.table) {
      return;
    }

    if (this.selectRow(value)) {
      return;
    }

    // TODO une seule requete pour les getPageNumber et setPage ??
    if (this.apiParams.prefilters?.includes('undefined')) {
      console.error('prefilter inconnu');
      return;
    }
    this._mData
      .getPageNumber(this.moduleCode(), this.objectCode(), value, this.apiParams)
      .subscribe((res) => {
        // set Page
        this.pageData = res;

        this.table.setPage(res.page);
      });
  }

  selectRow(value, fieldName: any = null) {
    if (!(value && this.table)) {
      return;
    }

    this.table.deselectRow();
    if (!fieldName) {
      fieldName = this.pkFieldName();
    }
    const row = this.table.getRows().find((row) => {
      return row.getData()[fieldName] == value;
    });
    if (row) {
      this.table.selectRow(row);
    }

    return !!row;
  }

  processConfig() {
    this.reDrawTable(true);
  }

  processFilters() {
    this.reDrawTable(true);
  }

  processPreFilters() {
    this.reDrawTable(true);
  }

  reDrawTable(force = false) {
    const elem = document.getElementById(this._id);
    if (!elem) {
      // on peut quand même récupérer les données (pour les label des tabs par exemple)
      if (!this.initCount) {
        this.initCount = true;
        this.processObject();
      }
      return;
    }
    if (!this.table) {
      this.drawTable();
    }

    this.tableHeight = `${elem.clientHeight}px`;
    this.table.setHeight(elem.clientHeight);
    const pageSize = Math.floor((elem.clientHeight - 90) / 50);

    const nbTotal = this._mObject.objectConfigContext(this.context).nb_total;

    if (
      (!this.computedLayout.page_size &&
        this.pageSize != pageSize &&
        nbTotal > pageSize &&
        pageSize > 1 &&
        !this.context.debug) ||
      force
    ) {
      this.pageSize = pageSize;
      this.drawTable();
    }
    this.setCount();
  }

  customParentsHeightChange(): void {
    if (!this.table) {
      this.drawTable();
    }

    // // si la taille du body n'a pas changé on retourne
    const tableHeight = parseInt(this.tableHeight?.replace('px', ''));
    const elementHeight = document.getElementById(this._id)?.clientHeight;
    if (this.table) {
      this.table.setHeight('100px');
    }

    this.reDrawTable();
  }

  getData(): Observable<any> {
    return this._mData.getList(this.moduleCode(), this.objectCode(), {
      fields: [this.pkFieldName()],
      only_info: true,
      filters: this.context.filters,
      prefilters: this.context.prefilters,
    });
  }

  refreshData(objectCode: any): void {
    if (objectCode == this.context.object_code) {
      this.reDrawTable();
    }
  }
}
