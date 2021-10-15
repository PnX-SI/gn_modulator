import { Component, OnInit, Input, SimpleChanges } from "@angular/core";
import { ActivatedRoute, Router, ParamMap } from "@angular/router";
import { mergeMap, concatMap } from "@librairies/rxjs/operators";
import { Observable, of, forkJoin } from "@librairies/rxjs";

import { HttpClient } from "@angular/common/http";
import { WidgetLibraryService } from 'angular7-json-schema-form';
import { ModulesConfigService } from "../../services/config.service"
import { ModulesDataService } from "../../services/data.service"

import { additionalWidgets } from './form-additional-widgets'

@Component({
  selector: "modules-base-form",
  templateUrl: "base-form.component.html",
  styleUrls: ["base-form.component.scss"],
})
export class BaseFormComponent implements OnInit {


  @Input() groupName = null;
  @Input() objectName = null;
  @Input() value = null;

  componentInitialized = false;
  schemaConfig = null;
  formTitle = null;
  data = null;

  additionalWidgets = additionalWidgets;

  constructor(
    private _route: ActivatedRoute,
    private _mConfig: ModulesConfigService,
    private _mData: ModulesDataService,
    private _widgetLibraryService: WidgetLibraryService
  ) {}


  ngOnInit() {

    // charge les widget additionels
    for (const [key, AdditionalWidget] of Object.entries(additionalWidgets)) {
      this._widgetLibraryService.registerWidget(key, AdditionalWidget);
    }

    this.process();

}

  process() {
    // load_config
    this._mConfig.loadConfig(this.groupName, this.objectName)
      .pipe(
        mergeMap((schemaConfig) => {
          this.schemaConfig = schemaConfig;
          return of(true)
        }),
        mergeMap(() => {
          return this._mData.getOne(this.groupName, this.objectName, this.value)
        }),
        mergeMap((data) => {
          this.data = data;
          this.setFormTitle();
          return of(true)
        })
      ).subscribe(() => {
        this.componentInitialized = true;
      });
  }

  id() {
      return this.data[this.schemaConfig.utils.pk_field_name];
  }

  setFormTitle() {
      this.formTitle = this.id()
        ? `Modification ${this.schemaConfig.display.def_label} ${this.id()}`
        : `Creation ${this.schemaConfig.display.undef_label_new}`
  }

  ngOnChanges(changes: SimpleChanges): void {
    this.process();
  }

  onSubmit($event) {
    let request = null;
    if (this.id()) {
        request = this._mData.patch(this.groupName, this.objectName, this.id(), this.data)
    } else {
        request = this._mData.post(this.groupName, this.objectName, this.data)
    }
    request.subscribe((data) => {
        this.data=data;
    });
  }
}

