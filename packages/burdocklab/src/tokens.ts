import {IWidgetTracker} from "@jupyterlab/apputils";
import {Token} from "@phosphor/coreutils";

import {BurdockPanel} from "./panel";

export const IBurdockTracker = new Token<IBurdockTracker>(
    '@burdocklab/burdocklab:IBurdockTracker'
);

export interface IBurdockTracker extends IWidgetTracker<BurdockPanel> {
}