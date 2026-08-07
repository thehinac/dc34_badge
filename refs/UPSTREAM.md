# Upstream sources used for this research

Clone these for full firmware context (not vendored here):

```text
https://github.com/bunnie/dc34-vault
https://github.com/bunnie/dc34-api
https://github.com/bunnie/dc34-console
https://github.com/betrusted-io/xous-core
https://github.com/baochip/baochip-1x
```

Key audit targets in vault:
- `src/main.rs` — `VaultOp::HandleQr`
- `src/actions.rs` — `acquire_qr`
- `src/config.rs` — gene cache, cipher, nonces
- `defcon-scheme.md` — mating protocol
