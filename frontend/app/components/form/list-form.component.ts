import { Component, OnInit, Input } from "@angular/core";
import { ListFormService } from "../../services/list-form.service";
import { ModulesLayoutComponent } from "../layout/layout.component";
import { ModulesLayoutService } from "../../services/layout.service";
import { FormArray, FormGroup, AbstractControl } from "@angular/forms";

import {
  mergeMap,
  startWith,
  pairwise,
  switchMap,
  debounceTime,
  distinctUntilChanged,
} from "@librairies/rxjs/operators";
import { of, Subject } from "@librairies/rxjs";

import utils from "../../utils";

@Component({
  selector: "modules-list-form",
  templateUrl: "list-form.component.html",
  styleUrls: ["../base/base.scss", "list-form.component.scss"],
})
export class ModulesListFormComponent
  extends ModulesLayoutComponent
  implements OnInit
{
  constructor(
    private _listFormService: ListFormService,
    _mLayout: ModulesLayoutService
  ) {
    super(_mLayout);
    this._name = "list_form"

  }

  items: any[] = [];
  // pour pouvoir filter en local
  itemsSave: any[] = [];
  nbItems;

  /** fonction de comparaison pour mat-select */
  compareFn;

  search = "";
  searchSubject: Subject<string>;
  searchSubscription = null;
  isLoading = false;

  @Input() formControl: AbstractControl = null;

  initSearch() {
    this.searchSubject = this.searchSubject || new Subject();
    this.searchSubscription && this.searchSubscription.unsubscribe();
    this.searchSubscription = this.searchSubject
      .pipe(
        distinctUntilChanged(),
        debounceTime(400 * this.computedLayout.reload_on_search)
      )
      .subscribe((search) => {
        this.processSearchChanged(search);
      });
  }


  getCompareFn = (return_object, value_field_name) => (a, b) => {
    return a && b && return_object
        ? a[value_field_name] ==
            b[value_field_name]
        : a == b;
  }
  /** initialisation du composant select */
  // postProcessLayout(): void {

  // }

  processListFormConfig() {
    this.initSearch();
    this.formControl = this.options.formGroup.get(this.layout.key);
    this.isLoading=true;
    this._listFormService
      .initListForm(this.computedLayout, this.formControl)
      .subscribe((infos) => {
        this.compareFn = this.getCompareFn(this.computedLayout.return_object, this.computedLayout.value_field_name);
        this.items = infos.items;
        this.nbItems = infos.nbItems;
        this.itemsSave = utils.copy(infos.items);
        this.isLoading=false;
      });
  }

  /** */
  postComputeLayout(): void {
    this.processListFormConfig();

  }

  /** action lorsque le champs de recherche change */
  searchChanged(event) {
    this.searchSubject.next(event);
  }

  /** processus de recherche dans les items */
  processSearchChanged(search) {
    if (this.computedLayout.reload_on_search) {
    // server side search ??
      this.computedLayout.search = search;
      this.isLoading = true;
      this._listFormService.getSelectList(this.computedLayout, this.formControl.value)
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
    if ([null, undefined, ""].includes(search)) {
      return this.itemsSave;
    }
    const searchLowerUnaccent = utils.lowerUnaccent(search);
    return this.itemsSave.filter((item) => {
      const label = utils.lowerUnaccent(
        item[this.computedLayout.label_field_name]
      );
      return label.includes(searchLowerUnaccent);
    });
  }

  /** remise à zéro de la selection */
  clearSelection() {
    this.formControl.patchValue(this.computedLayout.multiple ? [] : null);
  }
}
