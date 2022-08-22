import { CommonModule } from "@angular/common";
import { GN2CommonModule } from "@geonature_common/GN2Common.module";
import { Routes, RouterModule } from "@angular/router";
import {
  NgModule,
} from "@angular/core";

import { TestLayoutComponent } from "./components/test/test-layout.component";
import layoutComponents from "./components/layout"
import { ModulesIndexComponent } from "./components/index.component";
import { PageComponent } from "./components/page.component";
import { PageNotFoundComponent } from "./components/page-not-found.component";
import { BaseComponent } from "./components/base/base.component";
import { PageElementComponent } from "./components/base/page-element.component";
import { MaterialDesignFrameworkModule } from "@ajsf/material";
import ModulesServices from "./services/";
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
    ModulesIndexComponent,
    PageComponent,
    PageElementComponent,
    PageNotFoundComponent,
    TestLayoutComponent,
    ...layoutComponents,
  ],
  imports: [
    GN2CommonModule,
    RouterModule.forChild(routes),
    CommonModule,
    MaterialDesignFrameworkModule,
    MatTableModule,
    MatCheckboxModule
  ],
  exports: [
    ...layoutComponents
  ],
  providers: [
    ...ModulesServices
  ],
  bootstrap: [],
  entryComponents: [PageComponent],
})
export class GeonatureModule {}
