import { Component, OnInit, Injector } from "@angular/core";
import { Subscription } from "rxjs/Subscription";
import { ModulesConfigService } from "../../../services/config.service";
import { ModulesSchemaService } from "../../../services/schema.service";
import { ModulesDataService } from "../../../services/data.service";
import { ModulesPageService } from "../../../services/page.service";
import { ModulesObjectService } from "../../../services/object.service";
import { ModulesRouteService } from "../../../services/route.service";
import { ModulesLayoutComponent } from "../base/layout.component";
import { mergeMap, catchError } from "@librairies/rxjs/operators";
import { Observable, of } from "@librairies/rxjs";

/** Composant pour afficher des objets
 * layout
 *  - object_name: référence à object défini dans module.json
 *  - component:
 *    - map, table: liste d'object sur une carte
 *    - properties, form: pour 1 object (d'id=value)
 */
@Component({
  selector: "modules-layout-object",
  templateUrl: "layout-object.component.html",
  styleUrls: ["../../base/base.scss", "layout-object.component.scss"],
})
export class ModulesLayoutObjectComponent
  extends ModulesLayoutComponent
  implements OnInit
{
  schemaConfig; // configuration du schema TODO à enlever??
  moduleConfig; // configuration du module TODO à enlever??

  schemaData; // données relative au schema, récupérées par getData
  processedLayout; // layout pour form / details / etc..

  /** modules services */
  _mConfig: ModulesConfigService;
  _mSchema: ModulesSchemaService;
  _mData: ModulesDataService;
  _mRoute: ModulesRouteService;
  _mPage: ModulesPageService;
  _mObject: ModulesObjectService;

  /** subscription pour les informations sur les objects */
  _filtersSubscription: Subscription;
  _prefiltersSubscription: Subscription;
  _valueSubscription: Subscription;

  constructor(_injector: Injector) {
    super(_injector);
    this._mConfig = this._injector.get(ModulesConfigService);
    this._mData = this._injector.get(ModulesDataService);
    this._mSchema = this._injector.get(ModulesSchemaService);
    this._mRoute = this._injector.get(ModulesRouteService);
    this._mPage = this._injector.get(ModulesPageService);
    this._mObject = this._injector.get(ModulesObjectService);
    this._name = "layout-object";
  }

  ngOnDestroy() {
    this._filtersSubscription.unsubscribe();
    this._valueSubscription.unsubscribe();
    this._prefiltersSubscription.unsubscribe();
  }

  processObject() {
    // initialise les objects et les subscription à
    // - value
    // - filter
    // - TODO prefilter ?
    if (!(this._filtersSubscription && this._valueSubscription)) {
      // TODO une seule subscription ??
      // this._mPage.initObject(this.objectName())
      this._filtersSubscription = this._mObject
        .getObjectSubject(this.objectName(), "value")
        .subscribe((value) => {
          this.processValue(value);
        });
      this._prefiltersSubscription = this._mObject
        .getObjectSubject(this.objectName(), "prefilters")
        .subscribe((value) => {
          this.processPreFilters(value);
        });
      this._valueSubscription = this._mObject
        .getObjectSubject(this.objectName(), "filters")
        .subscribe((filters) => {
          this.processFilters(filters);
        });
    }
  }

  processValue(value) {
    this.postProcessLayout();
  }

  processFilters(filters) {
    this.postProcessLayout();
  }

  processPreFilters(prefilters) {
    this.postProcessLayout();
  }

  log(...args) {
    console.log(
      this._name,
      this.layout && this.layout.type,
      this.layout.component,
      this.layout.object_name,
      this._id,
      ...args
    );
  }

  /**
   * postProcessLayout
   *  - loadConfig: chargement de la configuration du schema
   *  - processConfig: traitement de la configuration (layout etc..)
   *  - getData: chargement des données
   *  - processData: traitement des données
   */
  postProcessLayout(): void {
    if (this.isProcessing) {
      return;
    }
    this.isProcessing = true;

    // initialise les subscription aux données d'object (si ce n'est pas déjà fait)
    this.processObject();

    // chargement de la configuration
    this._mConfig
      .loadConfig(this.schemaName())
      .pipe(
        mergeMap((schemaConfig) => {
          this.schemaConfig = schemaConfig;

          this.moduleConfig = this._mConfig.moduleConfig(
            this._mPage.moduleCode
          );
          // if (!!this._mPage.moduleCode) {
          //   this.moduleConfig = this._mConfig.moduleConfig(
          //     this._mPage.moduleCode
          //   );
          // }
          // traitement de la configuraiton
          this.processConfig();
          return of(true);
        }),

        mergeMap(() => {
          // recupération des données
          return this.getData();
        }),
        // gestion des erreurs
        catchError((error) => {
          this.isProcessing = false;
          return of(false);
        })
      )
      .subscribe((response) => {
        if (response) {
          // traitement des données
          this.processData(response);
        }
        // traitement terminé
        this.isProcessing = false;
      });
  }

  /** Traitement de la configuration */
  processConfig() {
    // cas du formulaire
    if (this.computedLayout.component == "form") {
      this.processedLayout = this._mSchema.processFormLayout(this.schemaConfig);
    }

    // cas des details ou propriété
    if (this.computedLayout.component == "properties") {
      this.processedLayout = this._mSchema.processPropertiesLayout(
        this.schemaConfig,
        this.moduleConfig
      );
    }

    // export ??
    if (this.computedLayout.component == "export") {
      this.processedLayout = {
        type: "button",
        title: "export",
        href: this._mPage.exportUrl(
          this._mPage.moduleCode,
          this.computedLayout.export_code
        ),
        description: "Exporter les données",
      };
    }
  }

  // traitement des données
  // peut être redefini
  processData(data) {
    this.schemaData = data;
  }

  // récupération des données
  // peut être redefini
  getData(): Observable<any> {
    if (
      ["form", "properties"].includes(this.computedLayout.component) &&
      this.getObjectValue()
    ) {
      return this.getOneRow();
    }
    return of({});
  }

  /**
   * getOneRow
   * Utilisé par detail et form (et autre ??)
   * pour récupérer un ligne identifiées par <id> = value
   */
  getOneRow() {
    const value = this.getObjectValue();
    if (!value) {
      return of(null);
    }

    const fields = this._mSchema.getFields(
      this.schemaName(),
      this.processedLayout
    );

    return this._mData.getOne(this.schemaName(), value, {
      fields,
    });
  }

  schemaName() {
    return this._mObject.getObjectValue(this.objectName(), "schema_name");
  }

  objectName() {
    return this.computedLayout.object_name;
  }

  // process des actions
  // TODO à clarifier avec page.element ??
  processAction(event) {
    if (
      ["submit", "cancel", "edit", "details", "create"].includes(event.action)
    ) {
      this._mPage.processAction(event.action, this.objectName(), {
        data: event.data,
        layout: this.processedLayout,
        value: event.data[this.pkFieldName()],
      });
    }
  }

  // champ de clé primaire
  pkFieldName() {
    return this._mSchema.pkFieldName(this.schemaName());
  }

  // champ pour le label
  labelFieldName() {
    return this._mSchema.labelFieldName(this.schemaName());
  }

  // valeur associée à l'id de l'object
  getObjectValue() {
    return this._mObject.getObjectValue(this.objectName(), "value");
  }

  // filtres associés à l'object
  getObjectFilters() {
    return this._mObject.getObjectValue(this.objectName(), "filters");
  }

  // prefiltres associés à l'object
  getObjectPreFilters() {
    return this._mObject.getObjectValue(this.objectName(), "prefilters");
  }
}
