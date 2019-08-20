import {IDisposable} from "@phosphor/disposable";
import {ISignal, Signal} from "@phosphor/signaling";

import {IBurdockInspector} from "./tokens";

export class BurdockInspectionHandler implements IDisposable, IBurdockInspector.IBurdockInspectable {
    private _disposed: Signal<this, void> = new Signal<this, void>(this);
    private _isDisposed: boolean = false;

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
}