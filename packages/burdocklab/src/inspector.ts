import {
    Panel,
    PanelLayout,
    Widget
} from "@phosphor/widgets";

import {
    Toolbar,
    ToolbarButton
} from "@jupyterlab/apputils";
import { IBurdockInspector } from "./tokens";

const PANEL_CLASS = 'jp-BurdockInspector';
const CONTENT_CLASS = 'jp-BurdockInspector-content';
const DEFAULT_CONTENT_CLASS = 'jp-BurdockInspector-default-content';

export class BurdockInspectorPanel extends Panel implements IBurdockInspector {
    private _source: IBurdockInspector.IInspectable | null;
    private _content: Widget = null;

    readonly toolbar: Toolbar;

    constructor(options: BurdockInspectorPanel.IOptions = {}) {
        super({...options} as Panel.IOptions);

        // this.title.iconClass =/
        this.title.closable = true;

        this.id = BurdockInspectorPanel.PANEL_ID;
        this.title.label = BurdockInspectorPanel.PANEL_TITLE;
        this.title.iconClass = "jp-SpreadsheetIcon";
        this.title.closable = true;

        const {initialContent} = options;

        if (initialContent instanceof Widget) {
            this._content = initialContent;
        } else if (typeof initialContent === 'string') {
            this._content = BurdockInspectorPanel._generateContentWidget(
                `<p>${options.initialContent}</p>`
            );
        } else {
            this._content = BurdockInspectorPanel._generateContentWidget(
                '<p>Click on a dataframe to see invariants.</p>'
            );
        }

        this.addClass(PANEL_CLASS);
        (this.layout as PanelLayout).addWidget(this._content);
    }

    get source(): IBurdockInspector.IInspectable | null {
        return this._source;
    }

    set source(source: IBurdockInspector.IInspectable | null) {
        if (this._source === source) return;

        // Disconnect any signal handlers.
        if (this._source) {
            this._source.standby = true;
            this._source.inspected.disconnect(this.onSourceInspected, this);
            this._source.disposed.disconnect(this.onSourceDisposed, this);
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
            this._source.inspected.connect(this.onSourceInspected, this);
            this._source.disposed.connect(this.onSourceDisposed, this);
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

    protected async onSourceInspected(sender: any, update: IBurdockInspector.IUpdate): Promise<void> {
        const {content} = update;

        if (!content || content === this._content) {
            return;
        }

        this._content.dispose();
        this._content = content;

        content.addClass(CONTENT_CLASS);
        (this.layout as PanelLayout).addWidget(content);
    }

    protected async onSourceDisposed(sender: any, args: void) {
        // Note, we explicitly want to call the setter here!
        this.source = null;
    }

    /**
     * Generate content widget from string
     */
    private static _generateContentWidget(message: string): Widget {
        const widget = new Widget();
        widget.node.innerHTML = message;
        widget.addClass(CONTENT_CLASS);
        widget.addClass(DEFAULT_CONTENT_CLASS);

        return widget;
    }
}

export namespace BurdockInspectorPanel {
    export const PANEL_ID = 'burdocklab-panel';
    export const PANEL_TITLE = 'Burdock Inspector';

    export interface IOptions {
        initialContent?: Widget | string | undefined;
    }
}