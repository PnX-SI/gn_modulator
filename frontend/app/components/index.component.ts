import { Component, OnInit, Input, SimpleChanges } from "@angular/core";

@Component({
  selector: "modules-index",
  templateUrl: "index.component.html",
  styleUrls: ["index.component.scss"],
})
export class ModulesIndexComponent implements OnInit {

  groups = [
    {
      title: 'Test',
      name: 'test',
      items: ['parent', 'child']
    },
    {
      title: 'Nomenclature',
      name: 'utils',
      items: ['nomenclature', 'nomenclature_type']
    },
    {
      title: 'Taxref',
      name: 'utils',
      items: ['taxref']
    },
    {
      title: 'Utilisateurs',
      name: 'utils',
      items: ['organisme', 'utilisateur']
    },
    {
      title: 'Synthese',
      name: 'utils',
      items: ['synthese']
    },

  ]

  constructor(
  ) {}

  ngOnInit() {
  }

}
