import {IWidgetTracker} from "@jupyterlab/apputils";
import {Token} from "@phosphor/coreutils";
import {BurdockPanel} from "./widget";

export const IBurdockTracker = new Token<IBurdockTracker>(
    '@burdocklab/core:IBurdockTracker'
);

export interface IBurdockTracker extends IWidgetTracker<BurdockPanel> {}