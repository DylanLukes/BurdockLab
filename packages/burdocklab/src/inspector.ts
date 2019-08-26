import {
    StackedPanel,
    Widget
} from "@phosphor/widgets";

import {
    Toolbar,
    ToolbarButton
} from "@jupyterlab/apputils";
import { IBurdockInspector } from "./tokens";

export class BurdockInspectorPanel extends StackedPanel implements IBurdockInspector {
    private _source: IBurdockInspector.IInspectable | null;

    readonly toolbar: Toolbar;

    constructor(options: BurdockInspectorPanel.IOptions = {}) {
        super({...options} as StackedPanel.IOptions);

        // this.title.iconClass =/
        this.title.closable = true;

        this.id = BurdockInspectorPanel.PANEL_ID;
        this.title.label = BurdockInspectorPanel.PANEL_TITLE;
        this.title.iconClass = "jp-SpreadsheetIcon";
        this.title.closable = true;
        this.addClass(BurdockInspectorPanel.PANEL_CLASS);


    }

    get source(): IBurdockInspector.IInspectable | null {
        return this._source;
    }

    set source(source: IBurdockInspector.IInspectable | null) {
        if (this._source === source) return;

        // Disconnect any signal handlers.
        if (this._source) {
            this._source.standby = true;
            // this._source.inspected.disconnect(this.onInspectorUpdate, this);
            // this._source.disposed.disconnect(this.onSourceDisposed, this);
        }

        // Reject a source that is already disposed.
        if (source && source.isDisposed) {
            console.warn("BurdockInspectorPanel was given a disposed source.");
            source = null;
        }

        // Update the source.
        this._source = source;

        // Connect any new signal handlers.
        if (this._source) {
            this._source.standby = false;
            // this._source.inspected.connect(this.onInspectorUpdate, this);
            // this._source.disposed.connect(this.onSourceDisposed, this);
        }
    }

    toolbarFactory(): Toolbar {
        const toolbar = new Toolbar<Widget>();

        let refreshButton = new ToolbarButton({
            tooltip: "Refresh from source",
            iconClassName: "jp-RefreshIcon jp-Icon jp-Icon-16",
            onClick: () => {
                alert("This doesn't work yet. Nice try.")
            }
        });

        toolbar.insertItem(0, 'refresh', refreshButton);

        return toolbar;
    }
}

export namespace BurdockInspectorPanel {
    export const PANEL_ID = 'burdocklab-panel';
    export const PANEL_CLASS = 'jp-BurdockInspectorPanel';
    export const PANEL_TITLE = 'Burdock Inspector';

    export interface IOptions {

    }
}