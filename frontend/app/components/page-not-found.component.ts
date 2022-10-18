import { Component, OnInit } from '@angular/core';
import { ModulesConfigService } from '../services/config.service';
import { ModulesRouteService } from '../services/route.service';
import { Router } from '@angular/router';
@Component({
  selector: 'modules-page',
  templateUrl: 'page-not-found.component.html',
  styleUrls: ['page-not-found.component.scss'],
})
export class PageNotFoundComponent implements OnInit {
  routesLoaded = false;

  constructor(
    private _mConfig: ModulesConfigService,
    private _mRoute: ModulesRouteService,
    private _router: Router
  ) {}

  ngOnInit() {
    if (this._mRoute.routesLoaded) {
      this.routesLoaded = true;
      return;
    }

    // si les pages ne spont pas encore chargées
    // - on s'assure qu'elles le soient avec _mRoute.initRoutes
    // - on recharge la page
    this._mRoute.initRoutes().subscribe(() => {
      this._mRoute.reloadPage();
    });
  }
}
