import { Component, Input, OnInit, SimpleChanges } from '@angular/core';
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

  @Input() height: string;

  @Input() center: Array<number>;
  @Input() zoom: number;

  @Input() layersData: any;

  @Input() mapId:string;

  @Input() bEdit: boolean = false;
  @Input() drawOptions;


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
    for (const [key, change] of Object.entries(changes)) {

      if(utils.fastDeepEqual(change['currentValue'], change['previousValue'])) {
        continue;
      }

      if(['zoom', 'center'].includes(key)) {
        this._mapService.setView(this.mapId, this.center, this.zoom)
      }

      if(['layersData'].includes(key)) {
        this.processLayersData()
      }
    }
  }
}