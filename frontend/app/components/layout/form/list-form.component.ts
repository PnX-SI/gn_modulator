import { Component, OnInit, Input, Injector } from '@angular/core';
import { ListFormService } from '../../../services/list-form.service';
import { ModulesLayoutComponent } from '../base/layout.component';
import { AbstractControl } from '@angular/forms';

import { debounceTime, distinctUntilChanged } from '@librairies/rxjs/operators';
import { Subject } from '@librairies/rxjs';

import utils from '../../../utils';

@Component({
  selector: 'modules-list-form',
  templateUrl: 'list-form.component.html',
  styleUrls: ['../../base/base.scss', 'list-form.component.scss'],
})
export class ModulesListFormComponent extends ModulesLayoutComponent implements OnInit {
  constructor(private _listFormService: ListFormService, _injector: Injector) {
    super(_injector);
    this._name = 'list_form';
    this.bPostComputeLayout = true;
  }

  items: any[] = [];
  // pour pouvoir filter en local
  itemsSave: any[] = [];
  nbItems;

  /** fonction de comparaison pour mat-select */
  compareFn;

  search = '';
  searchSubject: Subject<string>;
  searchSubscription = null;
  isLoading = false;

  listFormOptions;

  @Input() formControl: AbstractControl = null;

  initSearch() {
    this.searchSubject = this.searchSubject || new Subject();
    this.searchSubscription && this.searchSubscription.unsubscribe();
    this.searchSubscription = this.searchSubject
      .pipe(distinctUntilChanged(), debounceTime(400 * this.listFormOptions.reload_on_search))
      .subscribe((search) => {
        this.processSearchChanged(search);
      });
  }

  getCompareFn = (return_object, value_field_name) => (a, b) => {
    return a && b && return_object ? a[value_field_name] == b[value_field_name] : a == b;
  };
  /** initialisation du composant select */
  // postProcessLayout(): void {

  // }

  processListFormConfig() {
    this.listFormOptions = utils.copy(this.computedLayout);
    this.initSearch();
    this.formControl = this.getFormControl();
    this.isLoading = true;
    this._listFormService
      .initListForm(this.listFormOptions, this.formControl)
      .subscribe((infos) => {
        this.compareFn = this.getCompareFn(
          this.listFormOptions.return_object,
          this.listFormOptions.value_field_name
        );

        this.items = infos.items;
        this.nbItems = infos.nbItems;
        this.itemsSave = utils.copy(infos.items);
        this.isLoading = false;
        // mettre à jour l'affichage des données
      });
  }

  /** */
  postComputeLayout(dataChanged, layoutChanged): void {
    if (layoutChanged) {
      this.processListFormConfig();
    }
  }

  /** action lorsque le champs de recherche change */
  searchChanged(event) {
    this.searchSubject.next(event);
  }

  /** processus de recherche dans les items */
  processSearchChanged(search) {
    if (this.listFormOptions.reload_on_search) {
      // server side search ??
      this.listFormOptions.search = search;
      this.isLoading = true;
      this._listFormService
        .getSelectList(this.listFormOptions, this.formControl.value)
        .subscribe((infos) => {
          this.items = infos.items;
          this.nbItems = infos.nbItems;
          this.isLoading = false;
        });
    } else {
      // local search
      this.items = this.localSearch(search);
    }
  }

  /** Local search */
  localSearch(search) {
    if ([null, undefined, ''].includes(search)) {
      return this.itemsSave;
    }
    const searchLowerUnaccent = utils.lowerUnaccent(search);
    return this.itemsSave.filter((item) => {
      const label = utils.lowerUnaccent(item[this.listFormOptions.label_field_name]);
      return label.includes(searchLowerUnaccent);
    });
  }

  /** remise à zéro de la selection */
  clearSelection(event) {
    event.stopPropagation();
    this.formControl.patchValue(this.listFormOptions.multiple ? [] : null);
  }

  /** Quand le formulaire est modifié */
  inputChange() {
    this.listFormOptions.change && this.listFormOptions.change();
  }
}
