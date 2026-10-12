# familiarterm

A colorful ASCII creature that lives in your terminal and reacts to you.

## Install

```bash
./install.sh
```

## Use

```bash
familiarterm         # name = $USER\nfamiliarterm blob    # custom name
```

`q` or Ctrl+C to quit.

## What it reacts to

- **music playing** (mps mpris/playerctl) -> dances
- **you typing** -> happy / excited / love
- **CPU -> 60%** -> excited
- **22:00–06:00** -> sleeps
- **idle 45s+* -> tired

## Requires

- Python 3 (std /proc/stat)
- <code>playerctl</code> optional (for music reaction)

## License

MIT
