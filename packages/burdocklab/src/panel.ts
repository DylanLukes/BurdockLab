import {Panel} from "@phosphor/widgets";
import {ServiceManager} from "@jupyterlab/services";

export class BurdockPanel extends Panel {
    readonly manager: ServiceManager.IManager;

    constructor(options: BurdockPanel.IOptions) {
        super();
        this.addClass(BurdockPanel.PANEL_CLASS);

        let {
            manager
        } = options;

        this.manager = manager;

        // Todo: adapt this?
        // let session = (this._session = new ClientSession({
        //     manager: manager.sessions,
        //     path,
        //     name: name || `Console ${count}`,
        //     type: 'console',
        //     kernelPreference: options.kernelPreference,
        //     setBusy: options.setBusy
        // }));
    }
}

export namespace BurdockPanel {
    export const PANEL_CLASS = 'jp-BurdockPanel';

    export interface IOptions {
        manager: ServiceManager.IManager
    }
}