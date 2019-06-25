import {
    ILayoutRestorer,
    JupyterFrontEnd,
    JupyterFrontEndPlugin
} from '@jupyterlab/application';

import {
    ICommandPalette,
    WidgetTracker
} from '@jupyterlab/apputils';

import {
    ISettingRegistry
} from '@jupyterlab/coreutils';

import {
    DockLayout
} from "@phosphor/widgets";


import {CommandIDs} from "./commands";
import {IBurdockTracker} from "./tokens";
import {BurdockPanel} from "./widget";

import '../style/index.css';

function activateBurdock(
    app: JupyterFrontEnd,
    palette: ICommandPalette,
    restorer: ILayoutRestorer,
    // settingRegistry: ISettingRegistry
) {
    console.log('JupyterLab extension jupyter-burdock is activating!');

    const manager = app.serviceManager;
    const {commands, shell} = app;
    const category = 'Burdock';

    const tracker = new WidgetTracker<BurdockPanel>({namespace: 'burdock'});

    void restorer.restore(tracker, {
        command: CommandIDs.open,
        args: () => ({}),
        name: () => 'burdock', // todo: use something more unique?
        when: manager.ready
    });

    interface ICreateOptions extends Partial<BurdockPanel.IOptions> {
        /**
         * The tab insert mode.
         *
         * An insert mode is used to specify how a widget should be added
         * to the main area relative to a reference widget.
         */
        insertMode?: DockLayout.InsertMode;

        /**
         * Whether to activate the widget.  Defaults to `true`.
         */
        activate?: boolean;
    }

    async function createBurdock(options: ICreateOptions): Promise<BurdockPanel> {
        console.log("Creating Burdock!", options);

        await manager.ready;

        const panel = new BurdockPanel(manager);

        await tracker.add(panel);

        shell.add(panel, 'main', {
            mode: options.insertMode,
            activate: options.activate
        });
        return panel;
    }

    interface IOpenOptions extends Partial<BurdockPanel.IOptions> {
        /**
         * Whether to active the widget. Defaults to `true`.
         */
        activate?: boolean
    }

    commands.addCommand(CommandIDs.open, {
        label: 'Show Burdock',
        execute: (args: IOpenOptions) => {
            console.log("Open burdock called!", args);

            let widget = tracker.find(_ => true);

            if (widget) {
                if (!widget.isAttached) {
                    shell.add(widget, 'main')
                }

                if (args['activate'] !== false) {
                    shell.activateById(widget.id);
                }

                return widget;
            } else {
                return createBurdock(args);
            }
        }
    });

    [CommandIDs.open].forEach(command => {
        palette.addItem({command, category, args: {isPalette: true}});
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
        ISettingRegistry
    ],
    activate: activateBurdock,
    autoStart: true,
};

const plugins: JupyterFrontEndPlugin<any>[] = [trackerPlugin];
// noinspection JSUnusedGlobalSymbols
export default plugins;