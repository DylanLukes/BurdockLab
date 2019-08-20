import {Token} from "@phosphor/coreutils";
import { ISignal } from "@phosphor/signaling";

export const IBurdockInspector = new Token<IBurdockInspector>(
    '@burdocklab/burdocklab:IBurdockInspector'
);

export interface IBurdockInspector {
    source: IBurdockInspector.IBurdockInspectable | null;
}

export namespace IBurdockInspector {
    export interface IBurdockInspectable {
        /**
         * A signal emitted when the inspectable is disposed.
         */
        disposed: ISignal<any, void>;

        /**
         * Test whether the inspectable has been disposed.
         */
        isDisposed: boolean;
    }
}