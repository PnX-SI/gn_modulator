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
    if (this.processedLayout) {
      return;
    }
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
        },
        {
          flex: '0',
          code: 'utils.buttons_filter',
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
        const filterDef = filterDefs[key] || {};
        const field = filterDef?.field || key;
        let value = filterDef.key ? utils.getAttr(val, filterDef.key) : val;
        let type = filterDef?.type;
        if (Array.isArray(value)) {
          value = value.join(';');
          type = type || 'in';
        }

        type = type || '=';

        if (type == 'any' && val !== true) {
          value = null;
        }

        return {
          field,
          type,
          value,
        };
      })
      .filter(({ field, type, value }) => value != null && value !== '')
      .map(({ field, type, value }) => `${field} ${type} ${value}`)
      .join(', ');
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
