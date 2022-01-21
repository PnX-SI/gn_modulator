import { CommonModule } from '@angular/common';
import { GN2CommonModule } from "@geonature_common/GN2Common.module";
import { Routes,  RouterModule, Router } from "@angular/router";
import { NgModule, APP_BOOTSTRAP_LISTENER, APP_INITIALIZER } from '@angular/core';

import { TestComponent } from "./components/test.component";
import { ModulesIndexComponent } from "./components/index.component";
import { PageComponent } from "./components/page.component";
import { PageNotFoundComponent } from "./components/page-not-found.component";
import { ListFormComponent } from "./components/base/form"
import { BasePropertiesComponent } from "./components/base/base-properties.component";
import { BaseFormComponent } from "./components/base/base-form.component";
import { BaseTableComponent } from "./components/base/base-table.component";
import { BaseMapComponent } from "./components/base/base-map.component";
import { BaseFiltersComponent } from "./components/base/base-filters.component";
import { BaseComponent } from "./components/base/base.component";
import { ModulesMapListComponent } from "./components/base/map-list.component";
import { ModulesDebugComponent } from "./components/base/debug.component";
import { BaseLayoutComponent } from "./components/base/base-layout.component";
import { PageElementComponent } from "./components/base/page-element.component";
import { ModulesMapComponent } from "./components/base/map/map.component";

import { MaterialDesignFrameworkModule } from '@ajsf/material';

import { ModulesConfigService } from "./services/config.service";
import { ModulesRouteService } from "./services/route.service";
import { ModulesDataService } from "./services/data.service";
import { ModulesFormService } from "./services/form.service";
import { ModulesRequestService } from "./services/request.service";
import { ModulesMapService } from "./services/map.service";
import { ModulesTableService } from "./services/table.service";
import { ListFormService } from "./services/list-form.service";

import {
  MatTableModule
} from "@angular/material/table";


const routes: Routes = [
    { path: "", component: ModulesIndexComponent },
    { path: "test_schema", component: TestComponent },
    { path: "**", component: PageNotFoundComponent },
  ];
@NgModule({
  declarations: [
    BaseComponent,
    BaseFormComponent,
    BasePropertiesComponent,
    BaseTableComponent,
    BaseMapComponent,
    BaseFiltersComponent,
    ModulesIndexComponent,
    ModulesDebugComponent,
    PageComponent,
    BaseLayoutComponent,
    PageElementComponent,
    PageNotFoundComponent,
    TestComponent,
    ListFormComponent,
    ModulesMapComponent,
    ModulesMapListComponent
  ],
  imports: [
    GN2CommonModule,
    RouterModule.forChild(routes),
    CommonModule,
    MaterialDesignFrameworkModule,
    MatTableModule,
  ],
  // exports: [
  //   PageComponent
  // ],
  providers: [
    ModulesConfigService,
    ModulesDataService,
    ModulesFormService,
    ModulesRequestService,
    ListFormService,
    ModulesMapService,
    ModulesRouteService,
    ModulesTableService,
  ],
  bootstrap: [],
  entryComponents: [ListFormComponent, PageComponent]
})
export class GeonatureModule { }
