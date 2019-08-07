import {BurdockModel} from "./model";
import {VDomRenderer} from "@jupyterlab/apputils";
import * as React from 'react';
import {ServiceManager} from "@jupyterlab/services";
// import {Signal} from "@phosphor/signaling";

export class BurdockWidget extends VDomRenderer<BurdockModel> {
    private readonly _manager: ServiceManager;

    constructor(manager: ServiceManager, options?: BurdockWidget.IOptions) {
        super();

        this._manager = manager;
        console.log(this._manager);

        this.id = BurdockWidget.WIDGET_ID;
        this.title.label = BurdockWidget.WIDGET_TITLE;
        this.title.closable = true;
        this.addClass(BurdockWidget.WIDGET_CLASS);
    }

    protected render(): Array<React.ReactElement<any>> | React.ReactElement<any> | null {
        console.log("Rendering BurdockWidget!");
        return (
          <dl>
              <dt>Active Notebook Panel:</dt>
              <dd>undefined</dd>
              <dt>Active Kernel:</dt>
              <dd>undefined</dd>
              <dt>Test String:</dt>
              <dd>{this.model.testString}</dd>
          </dl>
        );
    }
}

export namespace BurdockWidget {
    export const WIDGET_ID = 'burdock-lab';
    export const WIDGET_CLASS = 'jp-BurdockWidget';

    export const WIDGET_TITLE = 'Burdock Lab';

    export interface IOptions {
        /** Doesn't do anything. */
        foo?: boolean
    }
}