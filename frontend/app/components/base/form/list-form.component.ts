import { AbstractControl } from '@angular/forms';
import { buildTitleMap, isArray } from '@ajsf/core';
import { Component, Input, OnInit } from '@angular/core';
import { JsonSchemaFormService } from '@ajsf/core';
import { HttpClient } from "@angular/common/http";
import { ListFormService } from '../../../services/list-form.service';
import { mergeMap } from "@librairies/rxjs/operators";
import { of } from "@librairies/rxjs";

@Component({
  selector: 'list-form',
  templateUrl: 'list-form.component.html',
  styles: [`
    mat-error { font-size: 75%; margin-top: -1rem; margin-bottom: 0.5rem; }
    ::ng-deep json-schema-form mat-form-field .mat-form-field-wrapper .mat-form-field-flex
      .mat-form-field-infix { width: initial; }
  `],
})
export class ListFormComponent implements OnInit {
  formControl: AbstractControl;
  controlName: string;
  controlValue: any;
  controlDisabled = false;
  boundControl = false;
  options: any;
  selectList: any[] = [];
  search = '';
  model=null;
  selectedItems: [];

  isArray = isArray;
  @Input() layoutNode: any;
  @Input() layoutIndex: number[];
  @Input() dataIndex: number[];

  constructor(
    private jsf: JsonSchemaFormService,
    private _listFormService: ListFormService
  ) { }

  ngOnInit() {
    this.options = this.layoutNode.options || {};
    // this.selectList = buildTitleMap(
    //   this.options.titleMap || this.options.enumNames,
    //   this.options.enum, !!this.options.required, !!this.options.flatList
    // );

    this.options.search = this.search;

    if (!this.options.notitle && !this.options.description && this.options.placeholder) {
      this.options.description = this.options.placeholder;
    }

    this.jsf.initializeControl(this, !this.options.readonly);

    /**
     * ici set time out pour temporiser après l'initialisation de jsf
     * et être sûr d'avoir une valeur pour controlValue (ou formControl.value0)
     */

    setTimeout(()=>{
    this._listFormService.initListForm(this.options, this.formControl.value)
      .subscribe(({selectList, model}) => {
        this.selectList = (selectList as any[]);
        this.model = model;
        // pour s'assurer du bon affichage
        setTimeout(() => {
          this.formControl.patchValue(this.formControl.value);
        });
    });
    });
//
        //   of(true)
    //   // this._listFormService
    //     // .formToModel(this.options, this.formControl.value)
    //     .pipe(
    //       // init list form config
    //       mergeMap(() => { return this._listFormService()}),
    //       mergeMap( (model) => {
    //         this.model = model;
    //         return this._listFormService
    //           .getSelectList(this.options, this.model)
    //       })
    //     ).subscribe((selectList)=>{
    //       this.selectList = selectList;
    //       // pour s'assurer du bon affichage
    //       this.formControl.patchValue(this.formControl.value)
    //     })
  }

  searchChanged(event) {
    if (this.options.data_reload_on_search && this.options.api && event != this.search) {
      this.search = event;
      this.options.search=event;
      this._listFormService.getSelectList(this.options, this.model).subscribe((selectList) => {
        this.selectList = selectList;
        this.jsf.updateValue(this, this.controlValue);
      })
    }
  }

  updateValue(event) {
    this.model = event;
    this.options.showErrors = true;

    const value = this._listFormService.modelToForm(this.options, this.model)


    this.jsf.updateValue(this, value);
  }
}
