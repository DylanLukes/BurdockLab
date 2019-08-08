import {Panel} from "@phosphor/widgets";
import {ServiceManager} from "@jupyterlab/services";
import {ClientSession, IClientSession} from "@jupyterlab/apputils";
import {UUID} from "@phosphor/coreutils";
import {IDisposable} from "@phosphor/disposable";

export class BurdockPanel extends Panel {
    readonly manager: ServiceManager.IManager;

    private readonly session: ClientSession;

    constructor(options: BurdockPanel.IOptions) {
        super();
        // this.title.iconClass =/
        this.title.closable = true;

        this.id = BurdockPanel.PANEL_ID;
        this.title.label = BurdockPanel.PANEL_TITLE;
        this.title.iconClass = "jp-SpreadsheetIcon";
        this.title.closable = true;
        this.addClass(BurdockPanel.PANEL_CLASS);

        let {
            path,
            basePath,
            manager
        } = options;

        let count = Private.count++;
        if (!path) {
            path = `${basePath || ''}/burdock-${count}-${UUID.uuid4()}`;
        }

        // todo: remove:
        this.title.label = path;

        this.manager = manager;

        this.session = new ClientSession({
            manager: manager.sessions,
            path,
            name: name || `Burdock ${count}`,
            type: 'console',
            kernelPreference: options.kernelPreference,
            setBusy: options.setBusy
        });

        void this.session;
        // this.session.kernelChanged.connect(void 0);
        // this.session.propertyChanged.connect(void 0);

    }
}

export namespace BurdockPanel {
    export const PANEL_ID = 'burdocklab-panel';
    export const PANEL_CLASS = 'jp-BurdockLabPanel';
    export const PANEL_TITLE = 'Burdock Lab';

    export interface IOptions {
        /** The path of an existing Burdock panel. **/
        readonly path?: string;

        /** The base path for a new console. **/
        readonly basePath?: string;

        /** The service manager used by the panel. */
        readonly manager: ServiceManager.IManager;

        /** A kernel preference. */
        kernelPreference?: IClientSession.IKernelPreference;

        /** A function to call when the kernel is busy. */
        setBusy?: () => IDisposable;
    }
}

/**
 * A namespace for private data.
 */
namespace Private {
    /**
     * The counter for new consoles.
     */
    export let count = 1;
}