# MPR

## Connecting via SSH

### 1. Add this to `~/.ssh/config`

```
Host bastion
  HostName bastion.ii.agh.edu.pl
  User lopacins
  IdentityFile ~/.ssh/id_ed25519_bastion

Host shell
  HostName shell.lab.ii.agh.edu.pl
  User lopacins
  ProxyCommand ssh -W %h:%p bastion
  IdentityFile ~/.ssh/id_ed25519_shell

Host vnode-01
  HostName vnode-01.lab.ii.agh.edu.pl
  User lopacins
  ProxyCommand ssh -W %h:%p shell
  IdentityFile ~/.ssh/id_ed25519_vnode
```

### 2. Use `Remote-SHH` extension to connect

- `CMD + Shift + P`
- Select `Remote-SSH - Connect to Host...`
- Select `vnode-01`
- Provide account password when prompted (3 times; be quick, there is very little time)
- If `ssh: connect to host bastion.ii.agh.edu.pl port 22: Connection refused` is displayed, wait until connection ban is removed
