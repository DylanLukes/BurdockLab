import { Token } from "@phosphor/coreutils";
import { ISignal } from "@phosphor/signaling";
import { Widget } from "@phosphor/widgets";

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

        /**
         * A signal emitted when an inspector value is generated.
         */
        inspected: ISignal<any, IBurdockInspectorUpdate>;

        /**
         * Indicates whether the inspectable source emits signals.
         *
         * #### Notes
         * The use case for this attribute is to limit the API traffic when no
         * inspector is visible. It can be modified by the consumer of the source.
         */
        standby: boolean;
    }

    export interface IBurdockInspectorUpdate {
        /**
         * The content being sent to the inspector for display.
         */
        content: Widget | null;
    }
}