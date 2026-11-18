# Pi and Gondolin smoke test

Date: 2026-11-18. Result: the basic test passed.

Pi ran on the host with GLM 5.3 through the configured z.ai provider.
Gondolin 0.14.0 ran the read, edit, write, and shell tools in a guest.
Pi was version 1.5.2. The extension came from Gondolin's main branch.

| Check | Result |
|---|---|
| Boot a guest | Pass, about four seconds in the boot check |
| Edit the mounted project | Pass, set the export format to lowercase `json` |
| Read an unrelated host file with the read tool | Blocked by the extension |
| Read that host file with the guest shell | File absent |
| Request an unrelated website | HTTP 403 with an empty host allowlist |
| Preserve the project for a second run | Pass |
| Start the second guest without the first guest's scratch file | Pass |

## Setup

The test used the existing Pi extension with one policy change. It passed
`createHttpHooks({ allowedHosts: [] }).httpHooks` to `VM.create`.
The model connection stayed on the host. Pi used a separate configuration
directory, no saved sessions, and disabled context discovery, MCP servers,
skills, and other extensions. Only the Gondolin extension was enabled.

The project directory was the only host directory mounted in the guest.
Each Pi process started and closed its own guest. The first run made five
tool calls. The second made two. Both processes exited successfully.

The test installed QEMU tools on the host after the first boot failed
because `qemu-img` was absent. The package manager configured the QEMU
packages but returned an error for an existing `audiveris` package.
The test used QEMU with KVM acceleration. A small privileged launcher gave
the test process the `kvm` group, then dropped to the agent user before
starting Node.js. It made no permanent change to group membership.

The test files, extension, launcher, and JSON event logs are under
`/tmp/oak-gondolin-smoke/`. Temporary storage can be cleared.

## Decision

Use this arrangement for the next small OAK comparison. It avoids a custom
guest image and allows the model connection to stay outside the guest.
This was a basic integration test. It did not measure parallel throughput,
test every file-access route, or restrict provider-side tools.

Source: [upstream extension](https://github.com/earendil-works/gondolin/blob/main/host/examples/pi-gondolin.ts).
