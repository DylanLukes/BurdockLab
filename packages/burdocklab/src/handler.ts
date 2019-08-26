import { IDisposable } from "@phosphor/disposable";
import {
    ISignal,
    Signal
} from "@phosphor/signaling";

import { IDataConnector } from "@jupyterlab/coreutils";
import { IRenderMimeRegistry } from "@jupyterlab/rendermime";
import { CodeEditor } from "@jupyterlab/codeeditor";

import { IBurdockInspector } from "./tokens";

import IInspectable = IBurdockInspector.IInspectable;
import IUpdate = IBurdockInspector.IUpdate;

export class BurdockInspectionHandler implements IDisposable, IInspectable {
    private _disposed: Signal<this, void> = new Signal<this, void>(this);
    private _isDisposed: boolean = false;
    private _inspected: Signal<any, IUpdate> = new Signal<any, IUpdate>(this);
    private _standby: boolean;

    private readonly _connector: IDataConnector<BurdockInspectionHandler.IReply, void, BurdockInspectionHandler.IRequest>;
    private readonly _rendermime: IRenderMimeRegistry;
    private _editor: CodeEditor.IEditor | null = null;

    constructor(options: BurdockInspectionHandler.IOptions) {
        this._connector = options.connector;
        this._rendermime = options.rendermime;

        void this._connector;
        void this._rendermime;
    }

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

    get inspected(): ISignal<any, IBurdockInspector.IUpdate> {
        return this._inspected;
    }

    get standby(): boolean {
        return this._standby;
    }

    set standby(value: boolean) {
        this._standby = value;
    }

    get editor(): CodeEditor.IEditor | null {
        return this._editor;
    }

    set editor(newEditor: CodeEditor.IEditor | null) {
        if (newEditor === this._editor) return;

        // Remove all listeners.
        Signal.disconnectReceiver(this);

        this._editor = newEditor;
        if(this._editor) {
            // this._cleared.emit(void 0);
            // this.onEditorChange();
            // editor.model.selections.changed.connect(this._onChange, this);
            // editor.model.value.changed.connect(this._onChange, this);
        }
    }
}

export namespace BurdockInspectionHandler {
    export interface IOptions {
        /**
         * The connector used to make inspection requests.
         *
         * #### Notes
         * The only method of this connector that will ever be called is `fetch`, so
         * it is acceptable for the other methods to be simple functions that return
         * rejected promises.
         */
        connector: IDataConnector<IReply, void, IRequest>;

        /**
         * The mime renderer for the inspection handler.
         */
        rendermime: IRenderMimeRegistry;
    }

    export interface IReply {

    }

    export interface IRequest {

    }
}