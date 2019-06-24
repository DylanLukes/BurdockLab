import {BurdockModel} from "./model";
import {VDomRenderer} from "@jupyterlab/apputils";
import * as React from 'react';
import {ServiceManager} from "@jupyterlab/services";

export class BurdockPanel extends VDomRenderer<BurdockModel> {
    private _manager: ServiceManager;

    constructor(manager: ServiceManager, options?: BurdockPanel.IOptions) {
        super();

        this._manager = manager;
        console.log(this._manager);

        this.id = BurdockPanel.WIDGET_ID;
        this.title.label = BurdockPanel.WIDGET_TITLE;
        this.title.closable = true;
        this.addClass(BurdockPanel.WIDGET_CLASS);
    }

    protected render(): Array<React.ReactElement<any>> | React.ReactElement<any> | null {
        console.log("Rendering BurdockPanel!");
        return (
          <p>Lorem ipsum dolor sit amet..?</p>
        );
    }
}

export namespace BurdockPanel {
    export const WIDGET_ID = 'burdock-lab';
    export const WIDGET_CLASS = 'jp-BurdockPanel';

    export const WIDGET_TITLE = 'Burdock Lab';

    export interface IOptions {
        /** Doesn't do anything. */
        foo?: boolean
    }
}