# download IndexTTS-2
```bash
uv tool install "huggingface-hub[cli,hf_xet]"

hf download IndexTeam/IndexTTS-2 --local-dir=checkpoints
```

**Note**
HuggingFace mirror
```bash
export HF_ENDPOINT="https://hf-mirror.com"
```

# check the data dir
must contains **cleaned voice** e.g. `test.wav`, **subtitle structure** e.g. `test_structural.json`, **remained background** e.g. `test_background.wav`

# about hf_envs.sh
that's a customized envs file that used on gpu platform, ignore it if you don't use a platform, modify it to suit your platform

# run demo
```bash
uv run main.py -v ./data/test.wav -s ./data/test_structural.json -b ./data/test_background.wav -o ./data/test_mixed.wav -t ./tmp -c /hy-tmp/checkpoints/config.yaml -m /hy-tmp/checkpoints
```