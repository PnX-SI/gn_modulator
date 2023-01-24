import { Component, OnInit, Injector } from '@angular/core';
import { ModulesLayoutObjectComponent } from './layout-object.component';
import utils from '../../../utils';

@Component({
  selector: 'modules-layout-object-filters',
  templateUrl: 'layout-object-filters.component.html',
  styleUrls: ['../../base/base.scss', 'layout-object-filters.component.scss'],
})
export class ModulesLayoutObjectFiltersComponent
  extends ModulesLayoutObjectComponent
  implements OnInit
{
  filterFormsData: any = {};
  filters: any = [];
  constructor(_injector: Injector) {
    super(_injector);
    this._name = 'layout-object-filters';
  }

  processConfig(): void {
    this.processedLayout = {
      height_auto: true,
      type: 'form',
      skip_required: true,
      appearance: 'outline',
      change:
        ({ data }) =>
        (event) =>
          this.processFiltersFormData(data),
      items: [
        {
          title: 'Filtres',
          flex: '0',
        },
        {
          items: this.layout.items,
          overflow: true,
        },
        {
          flex: '0',
          code: 'm_monitoring.buttons_filter',
        },
      ],
    };
  }

  processAction(event) {
    event.action == 'filter' && this.applyFilters();
    event.action == 'clear-filters' && this.clearFilters();
    this._mLayout.stopActionProcessing('');
  }

  processFiltersFormData(data) {
    const filterDefs = this.computedLayout.filter_defs;

    this.filters = Object.entries(data)
      .filter(([key, val]: any) => val != null)
      .map(([key, val]: any) => {
        const field = filterDefs[key]?.field || key;
        const type = filterDefs[key]?.type || '=';
        const value = filterDefs[key]?.key ? val[filterDefs[key].key] : utils.getAttr(data, key);
        return {
          field,
          type,
          value,
        };
      })
      .filter(({ field, type, value }) => value != null && value != '');
  }

  applyFilters() {
    this.setObject({ value: null, filters: this.filters });
  }

  clearFilters() {
    for (const key of Object.keys(this.filterFormsData)) {
      this.filterFormsData[key] = null;
    }
    const filterFormsData = utils.copy(this.filterFormsData);
    this.filterFormsData = null;
    setTimeout(() => {
      this.filterFormsData = filterFormsData;
      this.processFiltersFormData(this.filterFormsData);
      this.applyFilters();
    });
  }
}
