import { DataConnector } from "@jupyterlab/coreutils";
import { IClientSession } from "@jupyterlab/apputils";
import { BurdockInspectionHandler } from "./handler";

import IReply = BurdockInspectionHandler.IReply;
import IRequest = BurdockInspectionHandler.IRequest;

export class BurdockConnector extends DataConnector<IReply, void, IRequest> {
    private _session: IClientSession;

    constructor(options: BurdockConnector.IOptions) {
        super();
        this._session = options.session;
        void this._session;
    }

    fetch(id: IRequest): Promise<IReply | undefined>;
    fetch(id: IRequest): Promise<IReply | undefined>;
    fetch(id: IRequest): Promise<IReply | undefined> {
        return undefined;
    }
}

export namespace BurdockConnector {
    export interface IOptions {
        session: IClientSession;
    }
}