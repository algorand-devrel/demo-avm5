from pyteal import Int, Seq, Txn, Global, compileTeal, Return, OnComplete, Mode, Cond, Concat, Bytes, InnerTxnBuilder, TxnField, TxnType, And, Btoi

from util import itoa


def approval():

    is_app_creator = Txn.sender() == Global.creator_address()


    submit_inner_txn = And(
        is_app_creator,
        Seq(
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields({
                TxnField.type_enum: TxnType.AssetConfig,
                TxnField.config_asset_name: Txn.application_args[0],
                TxnField.config_asset_unit_name: Txn.application_args[1],
                TxnField.config_asset_manager: Global.current_application_address(),
                TxnField.config_asset_clawback: Global.current_application_address(),
                TxnField.config_asset_reserve: Global.current_application_address(),
                TxnField.config_asset_freeze: Global.current_application_address(),
                TxnField.config_asset_total: Btoi(Txn.application_args[2]),
                TxnField.config_asset_decimals: Int(0),
            }),
            InnerTxnBuilder.Submit(),
            Int(1)
        )
    )

    return Cond(
        [Txn.application_id() == Int(0),                        Return(Int(1))],
        [Txn.on_completion()  == OnComplete.DeleteApplication,  Return(is_app_creator)],
        [Txn.on_completion()  == OnComplete.UpdateApplication,  Return(is_app_creator)],
        [Txn.on_completion()  == OnComplete.CloseOut,           Return(Int(1))],
        [Txn.on_completion()  == OnComplete.OptIn,              Return(Int(1))],
        [Txn.on_completion()  == OnComplete.NoOp,               Return(submit_inner_txn)],
    )

def clear():
    return Return(Int(1))

if __name__ == "__main__":
    with open("approval.teal", "w") as f:
        f.write(compileTeal(approval(), mode=Mode.Application, version=5))

    with open("clear.teal", "w") as f:
        f.write(compileTeal(clear(), mode=Mode.Application, version=5))
