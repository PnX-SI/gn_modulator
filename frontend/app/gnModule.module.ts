import { NgModule } from "@angular/core";
import { CommonModule } from '@angular/common';
import { GN2CommonModule } from "@geonature_common/GN2Common.module";
import { Routes, RouterModule } from "@angular/router";
import { TestComponent } from "./components/test.component";
import { ModulesIndexComponent } from "./components/index.component";
import { BasePropertiesComponent } from "./components/base/base-properties.component";
import { BaseFormComponent } from "./components/base/base-form.component";
import { BaseTableComponent } from "./components/base/base-table.component";
import { MaterialDesignFrameworkModule } from 'angular7-json-schema-form';
import { ModulesConfigService } from "./services/config.service";
import { ModulesDataService } from "./services/data.service";

// my module routing
const routes: Routes = [
  { path: "", component: ModulesIndexComponent },
  { path: "test_schema/:moduleCode/:schemaName/:value", component: TestComponent },
];

@NgModule({
  declarations: [
    BaseFormComponent,
    BasePropertiesComponent,
    BaseTableComponent,
    ModulesIndexComponent,
    TestComponent,
  ],
  imports: [
    GN2CommonModule,
    RouterModule.forChild(routes),
    CommonModule,
    MaterialDesignFrameworkModule
  ],
  providers: [
    ModulesConfigService,
    ModulesDataService
  ],
  bootstrap: []
})
export class GeonatureModule { }
