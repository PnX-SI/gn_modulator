import { NgModule } from "@angular/core";
import { CommonModule } from '@angular/common';
import { GN2CommonModule } from "@geonature_common/GN2Common.module";
import { Routes, RouterModule } from "@angular/router";
import { TestComponent } from "./components/test.component";
import { ModulesIndexComponent } from "./components/index.component";
import { ListFormComponent } from "./components/base/form-additional-widgets"
import { BasePropertiesComponent } from "./components/base/base-properties.component";
import { BaseFormComponent } from "./components/base/base-form.component";
import { BaseTableComponent } from "./components/base/base-table.component";
import { MaterialDesignFrameworkModule } from 'angular7-json-schema-form';
import { ModulesConfigService } from "./services/config.service";
import { ModulesDataService } from "./services/data.service";
import { ModulesRequestService } from "./services/request.service";
import { ListFormService } from "./services/list-form.service";

import {
  MatTableModule
} from "@angular/material";


// my mo7ule routing
const routes: Routes = [
  { path: "", component: ModulesIndexComponent },
  { path: "test_schema/:groupName/:objectName/:value", component: TestComponent },
];

@NgModule({
  declarations: [
    BaseFormComponent,
    BasePropertiesComponent,
    BaseTableComponent,
    ModulesIndexComponent,
    TestComponent,
    ListFormComponent
  ],
  imports: [
    GN2CommonModule,
    RouterModule.forChild(routes),
    CommonModule,
    MaterialDesignFrameworkModule,
    MatTableModule
  ],
  providers: [
    ModulesConfigService,
    ModulesDataService,
    ModulesRequestService,
    ListFormService
  ],
  bootstrap: [],
  entryComponents: [ListFormComponent]
})
export class GeonatureModule { }
