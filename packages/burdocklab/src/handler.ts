import { IDisposable } from "@phosphor/disposable";
import {
    ISignal,
    Signal
} from "@phosphor/signaling";

import { IBurdockInspector } from "./tokens";
import IBurdockInspectorUpdate = IBurdockInspector.IBurdockInspectorUpdate;

export class BurdockInspectionHandler implements IDisposable, IBurdockInspector.IBurdockInspectable {
    private _disposed: Signal<this, void>
        = new Signal<this, void>(this);

    private _isDisposed: boolean = false;

    private _inspected: Signal<any, IBurdockInspectorUpdate>
        = new Signal<any, IBurdockInspectorUpdate>(this);

    private _standby: boolean;

    get disposed(): ISignal<this, void> {
        return this._disposed;
    }

    get isDisposed(): boolean {
        return this._isDisposed;
    }

    dispose(): void {
        if (this.isDisposed) return;
        this._isDisposed = true;
        this._disposed.emit(void 0);
        Signal.clearData(this);
    }

    get inspected(): ISignal<any, IBurdockInspectorUpdate> {
        return this._inspected;
    }

    get standby(): boolean {
        return this._standby;
    }

    set standby(value: boolean) {
        this._standby = value;
    }
}