# FamiliarGoof

An ASCII creature that lives in your terminal and reacts to you.

## Install

```bash
git clone https://github.com/Apersonwithtoenail/FamiliarGoof.git
cd FamiliarGoof
./install.sh
```

## Use

```bash
familiarterm         # name = $USER
familiarterm blob    # custom name
```

`q` or Ctrl+C to quit.

## What it reacts to

- music playing (via playerctl)  -> dances
- you typing                        -> happy / excited / love
- CPU > 60%                           -> excited
- 22:00–06:00                       -> sleeps
- idle 45s+                            -> tired

## Requires

- Python 3 (colors, TERM, /proc/stat)
- playerctl (optional — for music reaction)

## License

MIT
