from pyteal import Txn, Global, Ed25519Verify, Return, Int, Mode, OnComplete, Cond, compileTeal, Seq, Pop

def approval():
    is_app_creator = Txn.sender() == Global.creator_address()

    verify = Seq(
                Pop(Ed25519Verify(
                    Txn.application_args[0], 
                    Txn.application_args[1], 
                    Txn.sender()
                )),
                Int(1)
    )


    return Cond(
        [Txn.application_id() == Int(0),                        Return(Int(1))],
        [Txn.on_completion()  == OnComplete.DeleteApplication,  Return(is_app_creator)],
        [Txn.on_completion()  == OnComplete.UpdateApplication,  Return(is_app_creator)],
        [Txn.on_completion()  == OnComplete.CloseOut,           Return(Int(1))],
        [Txn.on_completion()  == OnComplete.OptIn,              Return(Int(1))],
        [Txn.application_args.length()>Int(0),                  Return(verify)],
        [Txn.application_args.length()==Int(0),                 Return(Int(1))]
    )

def clear():
    return Return(Int(1))

if __name__ == "__main__":
    with open("approval.teal", "w") as f:
        f.write(compileTeal(approval(), mode=Mode.Application, version=5))

    with open("clear.teal", "w") as f:
        f.write(compileTeal(clear(), mode=Mode.Application, version=5))
