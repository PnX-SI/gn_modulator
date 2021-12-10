import { Injectable } from "@angular/core";

import { AppConfig } from "@geonature_config/app.config";
import { ModuleConfig } from "../module.config";

import { of, Observable, Subject } from "@librairies/rxjs";
import { mergeMap, catchError } from "@librairies/rxjs/operators";
import { ModulesRequestService } from "./request.service";
import { ModulesConfigService } from "./config.service";
import { Routes,  RouterModule, Router } from "@angular/router";
import { PageComponent } from "../components/page.component";


@Injectable()
export class ModulesTableService {

  constructor(
  ) {
  }

}
