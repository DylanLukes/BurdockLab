import {ILayoutRestorer, JupyterFrontEnd, JupyterFrontEndPlugin} from '@jupyterlab/application';
import {IClientSession, ICommandPalette, WidgetTracker} from '@jupyterlab/apputils';
import {ISettingRegistry} from '@jupyterlab/coreutils';
import {IFileBrowserFactory} from "@jupyterlab/filebrowser";
import {INotebookTracker, NotebookPanel} from '@jupyterlab/notebook';

import {DockLayout} from '@phosphor/widgets';
import {find} from '@phosphor/algorithm';

import {BurdockPanel, CommandIDs, IBurdockTracker} from '@burdocklab/burdocklab';

import '../../burdocklab/style/index.css';

function activateBurdock(
    app: JupyterFrontEnd,
    palette: ICommandPalette,
    restorer: ILayoutRestorer,
    browserFactory: IFileBrowserFactory,
    settingRegistry: ISettingRegistry,
    notebooks: INotebookTracker
) {
    console.log('JupyterLab extension jupyter-burdock is activating!');

    const manager = app.serviceManager;
    const {commands, shell} = app;
    const category = 'Burdock';

    const tracker = new WidgetTracker<BurdockPanel>({namespace: 'burdock'});

    void restorer.restore(tracker, {
        command: CommandIDs.create,
        args: panel => ({
            path: panel.session.path,
            name: panel.session.name,
            kernelPreference: {
                name: panel.session.kernelPreference.name,
                language: panel.session.kernelPreference.name
            }
        }),
        name: panel => panel.session.path,
        when: manager.ready
    });

    interface ICreateOptions extends Partial<BurdockPanel.IOptions> {
        /** The reference widget id for the insert location.
         *  The default is `null`. */
        ref?: string | null;

        /** An insert mode is used to specify how a widget should be added
         *  to the main area relative to a reference widget. */
        insertMode?: DockLayout.InsertMode;

        /** Whether to activate the widget.  Defaults to `true`. */
        activate?: boolean;
    }

    async function createBurdock(options: ICreateOptions): Promise<BurdockPanel> {
        console.log("Creating Burdock!", options);

        await manager.ready;

        const panel = new BurdockPanel({
            manager,
             ...(options as Partial<BurdockPanel.IOptions>)
        });

        await tracker.add(panel);
        panel.session.propertyChanged.connect(() => tracker.save(panel));

        shell.add(panel, 'main', {
            ref: options.ref,
            mode: options.insertMode,
            activate: options.activate
        });
        return panel;
    }

    // Menu Items
    // ----------

    interface IOpenOptions extends Partial<BurdockPanel.IOptions> {
        /** Whether to active the widget. Defaults to `true`. */
        activate?: boolean
    }

    commands.addCommand(CommandIDs.open, {
        execute: (args: IOpenOptions) => {
            let path = args['path'];
            let panel = tracker.find(value => {
                return value.session.path === path;
            });

            if (panel) {
                if (args['activate'] !== false) {
                    shell.activateById(panel.id);
                }
                return panel;
            } else {
                return manager.ready.then(() => {
                    let model = find(manager.sessions.running(), session => {
                        return session.path === path;
                    });
                    if (model) {
                        return createBurdock(args);
                    }
                    return Promise.reject(`No running kernel session for path ${path}`);
                })
            }
        }
    });

    commands.addCommand(CommandIDs.create, {
        label: args => {
            if (args['isPalette']) {
                return 'New Burdock Panel';
            } else if (args['isLauncher'] && args['kernelPreference']) {
                const kernelPreference = args['kernelPreference'] as IClientSession.IKernelPreference;
                return manager.specs.kernelspecs[kernelPreference.name].display_name;
            }
            return 'Burdock Panel';
        },
        execute: args => {
            let basePath = (
                args['basePath'] as string ||
                args['cwd'] as string ||
                browserFactory.defaultBrowser.model.path
            );
            return createBurdock({basePath, ...args})
        }
    });

    [
        CommandIDs.create
    ].forEach(command => {
        palette.addItem({command, category, args: {isPalette: true}});
    });

    // Signal Management
    // -----------------

    notebooks.widgetAdded.connect((sender, nbPanel: NotebookPanel) => {
        console.log("ADDED: ", nbPanel);
    });

    notebooks.widgetUpdated.connect((sender, nbPanel: NotebookPanel) => {
        console.log("UPDATED: ", nbPanel);
    });

    notebooks.currentChanged.connect((sender, nbPanel: NotebookPanel) => {
        console.log("CURRENT: ", nbPanel);
        console.log("hello world!");
    });

    return tracker;
}

/**
 * Initialization data for the jupyter-burdock extension.
 */
const trackerPlugin: JupyterFrontEndPlugin<IBurdockTracker> = {
    id: '@burdocklab/core:tracker',
    provides: IBurdockTracker,
    requires: [
        ICommandPalette,
        ILayoutRestorer,
        IFileBrowserFactory,
        ISettingRegistry,
        INotebookTracker
    ],
    activate: activateBurdock,
    autoStart: true,
};

const plugins: JupyterFrontEndPlugin<any>[] = [trackerPlugin];
// noinspection JSUnusedGlobalSymbols
export default plugins;
