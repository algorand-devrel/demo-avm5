from pyteal import Int, Seq, Txn, Global, compileTeal, Return, OnComplete, Mode, Cond, Btoi, ScratchVar, For, TealType, Log, Concat, Bytes
from pyteal.ast.subroutine import Subroutine

from util import itoa


@Subroutine(TealType.none)
def sing(count):
    return Seq(
        Log(Concat(itoa(count), Bytes(" Bottles of beer on the wall"))),
        Log(Concat(itoa(count), Bytes(" Bottles of beer"))),
        Log(Bytes("Take one down, pass it around")),
        Log(Concat(itoa(count-Int(1)), Bytes(" Bottles of beer on the wall")))
    )

def approval():

    is_app_creator = Txn.sender() == Global.creator_address()

    i = ScratchVar()
    init = i.store(Int(99))
    cond = i.load()>Int(97)
    iter = i.store(i.load() - Int(1))

    log = Seq(
        For(init, cond, iter).Do(
            sing(i.load())
        ),
        Int(1)
    )

    return Cond(
        [Txn.application_id() == Int(0),                        Return(Int(1))],
        [Txn.on_completion()  == OnComplete.DeleteApplication,  Return(is_app_creator)],
        [Txn.on_completion()  == OnComplete.UpdateApplication,  Return(is_app_creator)],
        [Txn.on_completion()  == OnComplete.CloseOut,           Return(Int(1))],
        [Txn.on_completion()  == OnComplete.OptIn,              Return(Int(1))],
        [Txn.on_completion()  == OnComplete.NoOp,               Return(log)],
    )

def clear():
    return Return(Int(1))

if __name__ == "__main__":
    with open("approval.teal", "w") as f:
        f.write(compileTeal(approval(), mode=Mode.Application, version=5))

    with open("clear.teal", "w") as f:
        f.write(compileTeal(clear(), mode=Mode.Application, version=5))
