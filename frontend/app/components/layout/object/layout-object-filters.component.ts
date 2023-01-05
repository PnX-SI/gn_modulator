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
  filters: any = {};
  constructor(_injector: Injector) {
    super(_injector);
    this._name = 'layout-object-filters';
  }

  processConfig(): void {
    this.processedLayout = {
      height_auto: true,
      type: 'form',
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
          // items: this.objectConfig().filter_defs.form.layout,
          items: this.layout.items,
          overflow: true,
        },
        {
          flex: '0',
          direction: 'row',
          items: [
            {
              flex: '0',
              type: 'button',
              color: 'primary',
              title: 'Rechercher',
              icon: 'done',
              description: 'Effectuer une recherche avec les filtre définis ci-dessus',
              action: 'filter',
            },
            {
              flex: '0',
              type: 'button',
              color: 'primary',
              title: 'Réinitialiser',
              icon: 'refresh',
              description: 'RAZ des filtres',
              action: 'clear-filters',
            },
          ],
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
        let value = val;

        if (filterDefs.key) {
          value = val[filterDefs.key];
        }
        return {
          field,
          type,
          value,
        };
      });
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
      this.applyFilters();
    });
  }
}
