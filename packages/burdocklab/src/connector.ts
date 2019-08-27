import { DataConnector } from "@jupyterlab/coreutils";
import { IClientSession } from "@jupyterlab/apputils";
import { BurdockInspectionHandler } from "./handler";
import {
    Kernel, KernelMessage
} from "@jupyterlab/services";
import IReply = BurdockInspectionHandler.IReply;
import IRequest = BurdockInspectionHandler.IRequest;

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
        await comm.open();
        console.log("COMM OPEN", this._id);
        return comm;
    }

    async fetch(id: IRequest): Promise<IReply | undefined> {
        const comm = await this.ensureComm();

        return new Promise<IReply | undefined>((resolve, reject) => {
            const handler = comm.send({"hello": "world"});

            handler.onIOPub = (msg: KernelMessage.IIOPubMessage<'comm_msg'>) => {
                if (!KernelMessage.isCommMsgMsg(msg)) return;
                const {metadata, "content": {data}} = msg;

                resolve({
                    "data": data,
                    "metadata": metadata
                });
            };
        });
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