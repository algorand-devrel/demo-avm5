from pyteal import Txn, Global, Ed25519Verify, Return, Int, Mode, OnComplete, Cond, compileTeal, Seq, Pop

def approval():
    # Checks that the app call sender is the creator of this app
    is_app_creator = Txn.sender() == Global.creator_address()

    verify = Seq(
                Pop( # We don't actually care about the result of the verification function, just pop it off the stack
                    Ed25519Verify( # Calls the ed25519 verify opcode on what is normally some bytes that should be signed and the signature
                        Txn.application_args[0],  # Bytes signed
                        Txn.application_args[1],  # Signature
                        Txn.sender()              # Public key of signer
                    )
                ),
                # Return 1 so the transaction is approved
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
