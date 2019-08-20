import {VDomModel} from "@jupyterlab/apputils";

export class BurdockModel extends VDomModel {
    private _testString: string = "hello world!";

    get testString(): string {
        return this._testString;
    }

    set testString(newString: string) {
        this._testString = newString;
        this.stateChanged.emit(void 0);
    }
}

export namespace BurdockModel {

}