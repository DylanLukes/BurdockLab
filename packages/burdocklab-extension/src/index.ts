import {
    ILabShell,
    ILayoutRestorer,
    JupyterFrontEnd,
    JupyterFrontEndPlugin
} from '@jupyterlab/application';

import {
    ICommandPalette,
    MainAreaWidget,
    WidgetTracker
} from '@jupyterlab/apputils';

import { URLExt } from "@jupyterlab/coreutils";

import { IConsoleTracker } from '@jupyterlab/console';

import { INotebookTracker } from "@jupyterlab/notebook";

import {
    Kernel,
    KernelManager,
    ServerConnection
} from "@jupyterlab/services";

import { ILauncher } from "@jupyterlab/launcher";

import {
    BurdockInspectorPanel,
    CommandIDs,
    IBurdockInspector,
} from '@burdocklab/burdocklab';

import '../../burdocklab/style/index.css';

/**
 * A service providing Burdock (inspection).
 */
const inspector: JupyterFrontEndPlugin<IBurdockInspector> = {
    id: '@burdocklab/burdocklab-extension:inspector',
    optional: [
        ICommandPalette,
        ILauncher,
        ILayoutRestorer
    ],
    provides: IBurdockInspector,
    autoStart: true,
    activate: (
        app: JupyterFrontEnd,
        palette: ICommandPalette | null,
        launcher: ILauncher | null,
        restorer: ILayoutRestorer | null
    ): IBurdockInspector => {
        const {commands, shell} = app;
        const label = BurdockInspectorPanel.PANEL_TITLE;
        const namespace = 'burdocklab';
        const tracker = new WidgetTracker<MainAreaWidget<BurdockInspectorPanel>>({namespace});

        let source: IBurdockInspector.IBurdockInspectable | null = null;
        let inspector: MainAreaWidget<BurdockInspectorPanel>;

        async function openInspector(): Promise<MainAreaWidget<BurdockInspectorPanel>> {
            if (!inspector || inspector.isDisposed) {
                const panel = new BurdockInspectorPanel({});

                inspector = new MainAreaWidget<BurdockInspectorPanel>({
                    content: panel,
                    toolbar: panel.toolbarFactory()
                });

                await tracker.add(inspector);

                source = source && !source.isDisposed ? source : null;
                inspector.content.source = source;
            }

            if (!inspector.isAttached) {
                shell.add(inspector, 'main', {activate: false});
            }
            shell.activateById(inspector.id);

            return inspector;
        }

        const command = CommandIDs.open;
        commands.addCommand(command, {
            caption: 'Just a bunch of root vegetables',
            isEnabled: () =>
                !inspector ||
                inspector.isDisposed ||
                !inspector.isAttached ||
                !inspector.isVisible,
            label,
            iconClass: args => args.isLauncher ? 'jp-MaterialIcon jp-SpreadsheetIcon' : '',
            execute: () => openInspector()
        });

        if (palette) {
            palette.addItem({command, category: 'Burdock'});
        }

        if (launcher) {
            launcher.add({command, args: {isLauncher: true}})
        }

        if (restorer) {
            void restorer.restore(tracker, {
                command,
                name: () => namespace
            })
        }

        let proxy: IBurdockInspector;
        proxy = Object.defineProperty({}, 'source', {
            get: (): IBurdockInspector.IBurdockInspectable | null => {
                return !inspector || inspector.isDisposed ? null : inspector.content.source
            },
            set: (source: IBurdockInspector.IBurdockInspectable | null) => {
                source = source && !source.isDisposed ? source : null;
                if (inspector && !inspector.isDisposed) {
                    inspector.content.source = source;
                }
                // todo: should we be no-op'ing silently when it's missing?...
            }
        });

        return proxy;
    }
};

const notebooks: JupyterFrontEndPlugin<void> = {
    id: '@burdocklab/burdocklab-extension:notebooks',
    requires: [
        IBurdockInspector,
        INotebookTracker,
        ILabShell
    ],
    autoStart: true,
    activate: (
        app: JupyterFrontEnd,
        inspector: IBurdockInspector,
        notebooks: INotebookTracker,
        shell: ILabShell
    ) => {
        // const handlers = { [id: string]: BurdockHandler } = {};
        void app;
        void inspector;
        void notebooks;
        void shell;
    }
};

const consoles: JupyterFrontEndPlugin<void> = {
    id: '@burdocklab/burdocklab-extension:consoles',
    requires: [
        IBurdockInspector,
        IConsoleTracker,
        ILabShell
    ],
    autoStart: true,
    activate: (
        app: JupyterFrontEnd,
        inspector: IBurdockInspector,
        notebooks: INotebookTracker,
        shell: ILabShell
    ) => {
        // const handlers = { [id: string]: BurdockHandler } = {};
        void app;
        void inspector;
        void notebooks;
        void shell;
    }
};

/**
 * The kernels plugin detects changes in the set of running
 * kernels and ensures Burdock is installed in any Python3 kernels.
 */
const kernels: JupyterFrontEndPlugin<void> = {
    id: '@burdocklab/burdocklab-extension:kernels',
    requires: [
        IBurdockInspector
    ],
    autoStart: true,
    activate: (
        app: JupyterFrontEnd
    ) => {
        const manager = new KernelManager();

        function isSupported(kernel: Kernel.IModel): boolean {
            return kernel.name === 'python3';
        }

        async function isInstalled(kernel: Kernel.IModel): Promise<boolean> {
            const settings = ServerConnection.makeSettings({});
            const url = URLExt.join(settings.baseUrl, `api/burdock/${kernel.id}`);
            
            const response = await ServerConnection.makeRequest(url, {}, settings);
            return response.ok && (await response.json() !== false)
        }

        async function install(kernel: Kernel.IModel): Promise<Response> {
            const settings = ServerConnection.makeSettings({});
            const url = URLExt.join(settings.baseUrl, `api/burdock`);

            return await ServerConnection.makeRequest(url, {
                method: 'POST',
                body: JSON.stringify({
                    kernel_id: kernel.id
                })
            }, settings);
        }

        async function ensure(kernel: Kernel.IModel) {
            if (!isSupported(kernel)) {
                return
            }

            if (!(await isInstalled(kernel))) {
                await install(kernel);
            }
        }

        manager.runningChanged.connect(async (sender, kernels) => {
            for (let kernel of kernels) {
                await ensure(kernel);
            }
        })
    }
};

const plugins: JupyterFrontEndPlugin<any>[] = [
    inspector,
    notebooks,
    consoles,
    kernels
];
// noinspection JSUnusedGlobalSymbols
export default plugins;
