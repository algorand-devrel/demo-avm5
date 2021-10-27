AVM 1.0 Demos
-------------

See README in each demo file for details

Install `py-algorand-sdk` and `pyteal`

Install the sandbox from [here](https://github.com/algorand/sandbox)

> *Note*: These demos rely on a default unencrypted wallet in the kmd so only release/beta/nightly/dev sandbox configs will work

run `./sandbox up dev` to start the sandbox in dev mode (doesn't wait 4.5s for blocks)

ex of use:

```sh
cd op-pool # Or any of the examples
python app.py # Generates application.teal and clear.teal
python demo.py # Runs the demo
```

Happy Hacking  :)


