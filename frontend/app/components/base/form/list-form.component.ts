import { AbstractControl } from '@angular/forms';
import { buildTitleMap, isArray } from '@ajsf/core';
import { Component, Input, OnInit } from '@angular/core';
import { JsonSchemaFormService } from '@ajsf/core';
import { HttpClient } from "@angular/common/http";
import { ListFormService } from '../../../services/list-form.service';
import { FormArray, FormGroup, FormBuilder } from "@angular/forms";
import { mergeMap, startWith, pairwise } from "@librairies/rxjs/operators";
import { of } from "@librairies/rxjs";
import utils from "../../../utils"
@Component({
  selector: 'list-form',
  templateUrl: 'list-form.component.html',
  styleUrls: ['list-form.component.scss'],
})
export class ListFormComponent implements OnInit {
  formControl: AbstractControl;
  controlName: string;
  controlValue: any;
  controlDisabled = false;
  boundControl = false;
  options: any;
  selectList: any[] = [];

  // pour pouvoir filter en local
  selectListSave: any[] = [];


  search = '';
  model=null;
  selectedItems: [];

  isArray = isArray;
  @Input() layoutNode: any;
  @Input() layoutIndex: number[];
  @Input() dataIndex: number[];

  constructor(
    private jsf: JsonSchemaFormService,
    private _listFormService: ListFormService,
    private _fb: FormBuilder,
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

      // patch valeur init buggée
      if (this.options.return_object && this.options.multiple) {
        if (this.formControl.value.length == 1 && this.formControl.value[0][this.options.value_field_name] == null) {
          console.log(this.options.nomenclature_type, this.formControl.value);
          this.updateValue([]);

        }
      }

    this._listFormService.initListForm(this.options, this.formControl)
      .subscribe(({selectList, model}) => {
        this.selectList = (selectList as any[]);
        this.selectListSave = utils.copy(selectList as any[]);
        this.model = model;

        this.formControl.valueChanges
          .pipe(startWith(null as string), pairwise())
          .subscribe(([prev, next]: [any, any]) => {
            if(utils.fastDeepEqual(prev, next) && next != this.controlValue) {
              this.updateModel(next);
              return
            }
          });
      });
    });
  }

  updateModel(val) {
    return  this._listFormService.formToModel(this.options, val)
      .subscribe((model)=> {
        console.log(model)
        this.updateValue(model);
      });
  }

  searchChanged(event) {

    // passer par obsevable et debounce
    this.search = event;

    // filtrage server side
    if (this.options.data_reload_on_search && this.options.api && event != this.options.search) {
      this.options.search=event;
      this._listFormService.getSelectList(this.options, this.model).subscribe((selectList) => {
        this.selectList = selectList;
        this.jsf.updateValue(this, this.controlValue);
      })
    }
    // filtrage local
    else {
      const searchLowerUnaccent = utils.lowerUnaccent(this.search);
      this.selectList =this.selectListSave.filter(item => {
        const label = item[this.options.label_field_name].toLowerCase()
        return (
          !searchLowerUnaccent
          || utils.lowerUnaccent(label).includes(searchLowerUnaccent)
        )
      });
      // for (const item of this.selectList) {
      // }
    }
  }

  clearModel(event) {
    event.stopPropagation();
    this.updateValue(this.options.multiple ? [] : null);
  }

  onBlur(event) {
    this.options.showErrors = true;
  }

  updateValue(event) {
    console.log('updateValue', event);
    this.model = event;
    this.options.showErrors = true;
    let value = this._listFormService.modelToForm(this.options, this.model)

    // patch clear
    if (this.options.return_object && this.options.multiple) {
      const formArray = this.jsf.getFormControl(this) as FormArray;
      while (formArray.controls.length > 0) {
        formArray.removeAt(0);
      }
      value.forEach((v, i) => {
        formArray.setControl(i, this._fb.group(v))
        formArray.patchValue(value)
      });
    }

    this.jsf.updateValue(this, value);
  }
}
