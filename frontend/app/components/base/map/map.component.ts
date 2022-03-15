import { Component, Input, OnInit, SimpleChanges } from '@angular/core';
import { isInputRequired } from '@ajsf/core';
import { ModulesMapService } from "../../../services/map.service";
import utils from "../../../utils"
@Component({
  selector: 'modules-map',
  templateUrl: './map.component.html',
  styleUrls: [
    './map.component.scss'
  ],
})
export class ModulesMapComponent implements OnInit {

  @Input() height: string="600px";

  @Input() center: Array<number>;
  @Input() zoom: number;

  @Input() layersData: any;

  @Input() mapId:string;

  @Input() bEdit: boolean = false;
  @Input() drawOptions;

  @Input() isProcessing = false;

  isInitialized=false;

  constructor(
    private _mapService: ModulesMapService
  ) {}

  ngOnInit() {
    this._mapService.initMap(
      this.mapId,
      {
        center: this.center,
        zoom: this.zoom,
        bEdit: this.bEdit,
        drawOptions: this.drawOptions,
      }
    );
  }

  processLayersData() {
    this._mapService.waitForMap(this.mapId)
      .then(() => {
        this._mapService.processLayersData(this.mapId, this.layersData)
      });
  }

  ngOnChanges(changes: SimpleChanges): void {

    // attendre le chargement de la carte ?

    for (const [key, change] of Object.entries(changes)) {

      if(utils.fastDeepEqual(change['currentValue'], change['previousValue'])) {
        continue;
      }

      if(['zoom', 'center'].includes(key)) {
       this._mapService.setView(this.mapId, this.center, this.zoom);
      }

      if(['layersData'].includes(key)) {
        this.processLayersData()
      }

      if (key == 'drawOptions') {
        this._mapService.waitForMap((map) => { this._mapService.setDrawOptions(this.mapId, this.drawOptions)} );
      }

      if(key == 'height') {
        setTimeout(() => {
          this._mapService.waitForMap(this.mapId)
            .then((map) => { map.invalidateSize() });
        }, 500);
      }
    }
  }
}