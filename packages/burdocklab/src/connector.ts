import { DataConnector } from "@jupyterlab/coreutils";
import { IClientSession } from "@jupyterlab/apputils";
import { BurdockInspectionHandler } from "./handler";
import IReply = BurdockInspectionHandler.IReply;
import IRequest = BurdockInspectionHandler.IRequest;
import { KernelMessage, Kernel } from "@jupyterlab/services";

const TARGET_NAME = 'burdocklab_target';

export class BurdockConnector extends DataConnector<IReply, void, IRequest> {
    private _id: string;
    private _session: IClientSession;
    private _comm: Kernel.IComm | null;

    constructor(options: BurdockConnector.IOptions) {
        super();
        this._id = options.id;
        this._session = options.session;
    }

    async ensureComm(): Promise<Kernel.IComm> {
        if (this._comm && !this._comm.isDisposed) {
            return this._comm;
        }

        const {kernel} = this._session;
        if (!kernel) {
            return Promise.reject(new Error('Burdock inspection fetch requires a kernel.'));
        }

        const comm = (this._comm = kernel.connectToComm(TARGET_NAME, this._id));
        comm.onClose = this.onCommClose.bind(this);
        comm.onMsg = this.onCommMsg.bind(this);
        await comm.open();
        return comm;
    }

    async fetch(id: IRequest): Promise<IReply | undefined> {
        const comm = await this.ensureComm();
        const res = comm.send({"hello": "world"});

        console.log("RES:", res);
        return {
            "data": {},
            "metadata": {}
        };
    }

    async onCommClose(msg: KernelMessage.ICommCloseMsg): Promise<void> {
        console.log("COMM CLOSED", JSON.stringify(msg.content), this);
        this._comm.dispose();
        return;
    }

    async onCommMsg(msg: KernelMessage.ICommMsgMsg): Promise<void> {
        console.log("COMM MSG", JSON.stringify(msg.content), this);
        return;
    }
}

export namespace BurdockConnector {
    export interface IOptions {
        /** An identifier used to unique comms.
         * Nominally this is the notebook or console id. */
        id: string;

        session: IClientSession;
    }
}