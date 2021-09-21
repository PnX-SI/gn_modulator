import { Component, OnInit, Input, SimpleChanges } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { ActivatedRoute, Router, ParamMap } from "@angular/router";
import { ModulesConfigService } from "../../services/config.service"
import { ModulesDataService } from "../../services/data.service"
import { mergeMap, concatMap } from "@librairies/rxjs/operators";
import { Observable, of, forkJoin } from "@librairies/rxjs";

@Component({
  selector: "modules-base-form",
  templateUrl: "base-form.component.html",
  styleUrls: ["base-form.component.scss"],
})
export class BaseFormComponent implements OnInit {


  @Input() moduleCode = null;
  @Input() schemaName = null;
  @Input() value = null;

  componentInitialized = false;
  schemaConfig = null;
  formTitle = null;
  data = null;

  constructor(
    private _route: ActivatedRoute,
    private _mConfig: ModulesConfigService,
    private _mData: ModulesDataService
  ) {}


  ngOnInit() {

    // load_config
    this.process();
  }

  process() {
    // load_config
    this._mConfig.loadConfig(this.moduleCode, this.schemaName)
      .pipe(
        mergeMap((schemaConfig) => {
          this.schemaConfig = schemaConfig; 
          return of(true)
        }),
        mergeMap(() => {
          return this._mData.getOne(this.moduleCode, this.schemaName, this.value)
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
    console.log($event, this.data)
    let request = null;
    if (this.id()) {
        request = this._mData.patch(this.moduleCode, this.schemaName, this.id(), this.data)
    } else {
        request = this._mData.post(this.moduleCode, this.schemaName, this.data)
    }
    request.subscribe((data) => {
        console.log('request done', data)
        this.data=data;
    });
  }
}

