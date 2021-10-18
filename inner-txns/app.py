from pyteal import Int, Seq, Txn, Global, compileTeal, Return, OnComplete, Mode, Cond, Concat, Bytes, InnerTxnBuilder, TxnField, TxnType, And, Btoi
import os

from util import itoa


# The logic for the approval program returned from this function
def approval():

    # Checks that the sender is the app creator
    is_app_creator = Txn.sender() == Global.creator_address()

    # This is the main functionality of this app
    submit_inner_txn = And(
        is_app_creator, # First check that the sender is the app creator
        Seq(            # Seq is used to group a set of operations with only the last returning a value on the stack 

            # Start to build the transaction builder
            InnerTxnBuilder.Begin(),    

            # This method accepts a dictionary of TxnField to value so all fields may be set 
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

            # Submit the transaction we just built
            InnerTxnBuilder.Submit(),

            # Return 1 so the outer And evaluates to true
            Int(1)
        )
    )

    # Generic boilerplate router for an application to handle the different OnComplete settings
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
    path = os.path.dirname(os.path.abspath(__file__))

    with open(os.path.join(path,"approval.teal"), "w") as f:
        f.write(compileTeal(approval(), mode=Mode.Application, version=5))

    with open(os.path.join(path,"clear.teal"), "w") as f:
        f.write(compileTeal(clear(), mode=Mode.Application, version=5))
