import {BurdockModel} from "./model";
import {VDomRenderer} from "@jupyterlab/apputils";
import * as React from 'react';
import {ServiceManager} from "@jupyterlab/services";
// import {Signal} from "@phosphor/signaling";

export class BurdockWidget extends VDomRenderer<BurdockModel> {
    private readonly manager: ServiceManager.IManager;

    constructor(manager: ServiceManager.IManager, options?: BurdockWidget.IOptions) {
        super();

        this.manager = manager;
        void this.manager;

        this.id = BurdockWidget.WIDGET_ID;
        this.title.label = BurdockWidget.WIDGET_TITLE;
        this.title.closable = true;
        this.addClass(BurdockWidget.WIDGET_CLASS);
    }

    protected render(): Array<React.ReactElement<any>> | React.ReactElement<any> | null {
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
    export const WIDGET_ID = 'burdocklab-widget';
    export const WIDGET_CLASS = 'jp-BurdockLabWidget';

    export const WIDGET_TITLE = 'Burdock Lab';

    export interface IOptions {
        /** Doesn't do anything. */
        // foo?: boolean
    }
}