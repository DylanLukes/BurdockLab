import {
  JupyterLab, JupyterLabPlugin, ILayoutRestorer
} from '@jupyterlab/application';

import {
  ICommandPalette, InstanceTracker
} from '@jupyterlab/apputils';

import {
  JSONExt
} from '@phosphor/coreutils';

import {
  Message
} from '@phosphor/messaging';

import {
  Widget
} from '@phosphor/widgets';

import '../style/index.css';


class BurdockWidget extends Widget {
  readonly text: HTMLParagraphElement;

  constructor() {
    super();

    this.id = 'burdock-jupyterlab';
    this.title.label = 'Burdock';
    this.title.closable = true;
    this.addClass('jp-BurdockWidget');

    this.text = document.createElement('p')
    this.text.innerText = "Has anyone really been far even as decided to use even go want to do look more like?"
    this.text.style.padding = "50px";
    this.node.appendChild(this.text);
  }

  onUpdateRequest(msg: Message) {
    
  }
}

function activate(
  app: JupyterLab,
  palette: ICommandPalette,
  restorer: ILayoutRestorer
) {
  console.log('JupyterLab extension jupyter-burdock is activated!');

  let widget: BurdockWidget;

  let tracker = new InstanceTracker<Widget>({
    namespace: 'burdock'
  });
  
  const command: string = 'burdock:open';
  app.commands.addCommand(command, {
    label: 'Open the Burdock viewer',
    execute: () => {
      if (!widget) {
        widget = new BurdockWidget();
        widget.update();
      }

      if (!tracker.has(widget)) {
        tracker.add(widget);
      }

      if (!widget.isAttached) {
        app.shell.addToMainArea(widget, {
          mode: 'split-bottom'
        });
      } else {
        widget.update();
      }

      app.shell.activateById(widget.id);
    }
  });

  palette.addItem({ command, category: 'Burdock' });

  restorer.restore(tracker, {
    command,
    args: () => JSONExt.emptyObject,
    name: () => 'burdock'
  })
}

/**
 * Initialization data for the jupyter-burdock extension.
 */
const extension: JupyterLabPlugin<void> = {
  id: 'jupyter-burdock',
  autoStart: true,
  requires: [ICommandPalette, ILayoutRestorer],
  activate: activate
};

export default extension;
