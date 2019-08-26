import { IDisposable } from "@phosphor/disposable";
import {
    ISignal,
    Signal
} from "@phosphor/signaling";

import {
    Debouncer,
    IDataConnector,
    Text
} from "@jupyterlab/coreutils";
import {
    IRenderMimeRegistry,
    MimeModel
} from "@jupyterlab/rendermime";
import { CodeEditor } from "@jupyterlab/codeeditor";

import { IBurdockInspector } from "./tokens";
import { ReadonlyJSONObject } from "@phosphor/coreutils";
import IInspectable = IBurdockInspector.IInspectable;
import IUpdate = IBurdockInspector.IUpdate;

const DEBOUNCER_LIMIT = 250;

export class BurdockInspectionHandler implements IDisposable, IInspectable {
    private _cleared: Signal<this, void> = new Signal<this, void>(this);
    private _disposed: Signal<this, void> = new Signal<this, void>(this);
    private _isDisposed: boolean = false;
    private _pending: number = 0;
    private _inspected: Signal<any, IUpdate> = new Signal<any, IUpdate>(this);
    private _standby: boolean;
    private _debouncer: Debouncer;

    private readonly _connector: IDataConnector<BurdockInspectionHandler.IReply, void, BurdockInspectionHandler.IRequest>;
    private readonly _rendermime: IRenderMimeRegistry;
    private _editor: CodeEditor.IEditor | null = null;

    constructor(options: BurdockInspectionHandler.IOptions) {
        this._connector = options.connector;
        this._rendermime = options.rendermime;
        this._debouncer = new Debouncer(this.onEditorChange.bind(this), DEBOUNCER_LIMIT);
    }

    get cleared(): Signal<this, void> {
        return this._cleared;
    }

    set cleared(value: Signal<this, void>) {
        this._cleared = value;
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

        const editor = (this._editor = newEditor);
        if (editor) {
            this._cleared.emit(void 0);
            this.onEditorChange().then(() => {
                editor.model.selections.changed.connect(this._onChange, this);
                editor.model.value.changed.connect(this._onChange, this);
            });
        }
    }

    protected async onEditorChange(): Promise<void> {
        if (this._standby) return;

        const editor = this.editor;

        if (!editor) return;

        const {text} = editor.model.value;
        const position = editor.getCursorPosition();
        const offset = Text.jsIndexToCharIndex(editor.getOffsetAt(position), text);
        const update: IBurdockInspector.IUpdate = {content: null};

        const pending = ++this._pending;

        try {
            const reply = await this._connector.fetch({offset, text});

            // If handler has been disposed or a newer request is pending, bail.
            if (this.isDisposed || pending !== this._pending) {
                this._inspected.emit(update);
                return;
            }

            const {data} = reply;
            const mimeType = this._rendermime.preferredMimeType(data);

            if (mimeType) {
                const widget = this._rendermime.createRenderer(mimeType);
                const model = new MimeModel({data});

                await widget.renderModel(model);
                update.content = widget;

                this._inspected.emit(update);
            }

        } catch (_err) {
            // Since almost all failures are benign, fail silently.
            this._inspected.emit(update);
        }
    }

    private _onChange(): void {
        void this._debouncer.invoke();
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
         * todo: is this accurate for Burdock?
         */
        connector: IDataConnector<IReply, void, IRequest>;

        /** The mime renderer for the inspection handler. */
        rendermime: IRenderMimeRegistry;
    }

    /** A reply to an inspection request. */
    export interface IReply {
        /** The MIME bundle data returned from an inspection request. */
        data: ReadonlyJSONObject;

        /** Any metadata that accompanies the MIME bundle returning from a request. */
        metadata: ReadonlyJSONObject;
    }

    /** The details of an inspection request. */
    export interface IRequest {
        /** The cursor offset position within the text being inspected. */
        offset: number;

        /** The text being inspected. */
        text: string;
    }
}