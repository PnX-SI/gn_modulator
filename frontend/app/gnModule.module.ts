import { CommonModule } from "@angular/common";
import { GN2CommonModule } from "@geonature_common/GN2Common.module";
import { Routes, RouterModule, Router } from "@angular/router";
import {
  NgModule,
  APP_BOOTSTRAP_LISTENER,
  APP_INITIALIZER,
} from "@angular/core";

import { TestLayoutComponent } from "./components/test/test-layout.component";
import { ModulesLayoutComponent } from "./components/layout/layout.component";
import { ModulesLayoutSectionComponent } from "./components/layout/layout-section.component";
import { ModulesLayoutKeyComponent } from "./components/layout/layout-key.component";
import { ModulesLayoutArrayComponent } from "./components/layout/layout-array.component";
import { ModulesLayoutObjectComponent } from "./components/layout/layout-object.component";
import { ModulesGenericFormComponent } from "./components/form/generic-form.component";
import { ModulesFormElementComponent } from "./components/form/form-element.component";
import { ModulesListFormComponent } from "./components/form/list-form.component";
import { ModulesIndexComponent } from "./components/index.component";
import { PageComponent } from "./components/page.component";
import { PageNotFoundComponent } from "./components/page-not-found.component";
import { BasePropertiesComponent } from "./components/base/base-properties.component";
import { BaseFormComponent } from "./components/base/base-form.component";
import { BaseTableComponent } from "./components/base/base-table.component";
import { BaseMapComponent } from "./components/base/base-map.component";
import { BaseFiltersComponent } from "./components/base/base-filters.component";
import { BaseComponent } from "./components/base/base.component";
import { ModulesMapListComponent } from "./components/base/map-list.component";
import { ModulesDebugComponent } from "./components/base/debug.component";
import { PageElementComponent } from "./components/base/page-element.component";
import { ModulesMapComponent } from "./components/base/map/map.component";

import { MaterialDesignFrameworkModule } from "@ajsf/material";

import { ModulesConfigService } from "./services/config.service";
import { ModulesRouteService } from "./services/route.service";
import { ModulesDataService } from "./services/data.service";
import { ModulesService } from "./services/all.service";
import { ModulesLayoutService } from "./services/layout.service";
import { ModulesFormService } from "./services/form.service";
import { ModulesRequestService } from "./services/request.service";
import { ModulesMapService } from "./services/map.service";
import { ModulesTableService } from "./services/table.service";
import { ListFormService } from "./services/list-form.service";

import { MatTableModule } from "@angular/material/table";
import { MatCheckboxModule } from "@angular/material/checkbox";

const routes: Routes = [
  { path: "", component: ModulesIndexComponent },
  { path: "test_layout", component: TestLayoutComponent },
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
    ModulesFormElementComponent,
    ModulesGenericFormComponent,
    ModulesLayoutComponent,
    ModulesLayoutSectionComponent,
    ModulesLayoutKeyComponent,
    ModulesLayoutArrayComponent,
    ModulesLayoutObjectComponent,
    ModulesListFormComponent,
    PageComponent,
    PageElementComponent,
    PageNotFoundComponent,
    TestLayoutComponent,
    ModulesMapComponent,
    ModulesMapListComponent,
  ],
  imports: [
    GN2CommonModule,
    RouterModule.forChild(routes),
    CommonModule,
    MaterialDesignFrameworkModule,
    MatTableModule,
    MatCheckboxModule
  ],
  // exports: [
  //   PageComponent
  // ],
  providers: [
    ModulesConfigService,
    ModulesDataService,
    ModulesService,
    ModulesLayoutService,
    ModulesFormService,
    ModulesRequestService,
    ListFormService,
    ModulesMapService,
    ModulesRouteService,
    ModulesTableService,
  ],
  bootstrap: [],
  entryComponents: [PageComponent],
})
export class GeonatureModule {}
