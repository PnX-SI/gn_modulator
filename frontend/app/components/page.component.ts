import { Component, OnInit, Injector } from "@angular/core";
import { ModulesConfigService } from "../services/config.service";
import { ModulesPageService } from "../services/page.service";
import { ModulesObjectService } from "../services/object.service";
import { ActivatedRoute } from "@angular/router";
import utils from "../utils";

@Component({
  selector: "modules-page",
  templateUrl: "page.component.html",
  styleUrls: ["base/base.scss", "page.component.scss"],
})
export class PageComponent implements OnInit {
  // services
  _mConfig: ModulesConfigService;
  _route: ActivatedRoute;
  _mPage: ModulesPageService;
  _mObject: ModulesObjectService;

  debug = false; // pour activer le mode debug (depuis les queryParams)

  moduleConfig; // configuration du module
  pageConfig; // configuration de la route en cours
  pageName; // nom (ou code de la page)
  moduleCode; // code du module en cours
  layout; // layout de la page (récupéré depuis pageConfig.layout_name)
  data = {}; // data pour le layout

  pageInitialized: boolean; // test si la page est initialisée (pour affichage)

  constructor(private _injector: Injector) {
    this._route = this._injector.get(ActivatedRoute);
    this._mConfig = this._injector.get(ModulesConfigService);
    this._mPage = this._injector.get(ModulesPageService);
    this._mObject = this._injector.get(ModulesObjectService);
  }

  ngOnInit() {
    // routeData => { pageName, moduleCode }
    this._route.data.subscribe((routeData) => {

      this.pageName = routeData.pageName;
      this.moduleCode = routeData.moduleCode;

      // pour pouvoir retrouver moduleCode par ailleurs
      this._mPage.moduleCode = routeData.moduleCode;

      // recupéraiton de la configuration de la page;
      this.moduleConfig = this._mConfig.moduleConfig(this.moduleCode);
      this.pageConfig = this.moduleConfig.pages[this.pageName];

      // initialisatio du layout
      this.layout = {
        layout_name: this.pageConfig.layout_name,
      };

      this._mObject.resetObjects();

      // pour définir les schema_name des objects (et autres ???)
      this._mObject.processPageObjectParams(this.moduleConfig.objects);

      // lien entre les paramètres
      // en passant par le service mPage
      // permet de récupérer value
      // - id de l'objet en cours ? (par ex. id d'un site)
      // - paramètre de prefilter pour des liste d'objet (par ex. visite d'un site)
      this._route.params.subscribe((params) => {
        this._mObject.processPageObjectParams(this.pageConfig.params, params);
      });

      // queryParams
      // - debug: affichage graphique de la configuraiton des layouts
      this._route.queryParams.subscribe((params) => {
        this.debug = ![undefined, false, "false"].includes(params.debug);
      });

      this.pageInitialized = true
    });
  }

  /** TODO
   * - à déplacer ailleurs
   * - object_name (trouver plus pertinent)
   * Action de page
   * - lien vers d'autres pages
   * - route de validation de formulaires
   */
  processAction(event) {
    this._mPage.processAction(
      event.action,
      event.layout.object_name,
      event.layout
    );
  }
}
