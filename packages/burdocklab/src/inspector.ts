import {Panel, Widget} from "@phosphor/widgets";
import {
    Toolbar,
    ToolbarButton
} from "@jupyterlab/apputils";
import {IBurdockInspector} from "./tokens";

export class BurdockInspectorPanel extends Panel implements IBurdockInspector {
    public source: IBurdockInspector.IBurdockInspectable;

    readonly toolbar: Toolbar;

    constructor(options: BurdockInspectorPanel.IOptions = {}) {
        super(options);

        // this.title.iconClass =/
        this.title.closable = true;

        this.id = BurdockInspectorPanel.PANEL_ID;
        this.title.label = BurdockInspectorPanel.PANEL_TITLE;
        this.title.iconClass = "jp-SpreadsheetIcon";
        this.title.closable = true;
        this.addClass(BurdockInspectorPanel.PANEL_CLASS);

        let hello = document.createElement('h1');
        hello.innerText = "Hello, Burdock!";
        this.node.appendChild(hello);
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

    export interface IOptions extends Panel.IOptions {

    }
}