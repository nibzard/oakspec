# Website handoff pilot

Date: 2026-11-18. The test used `claude-zai -p` with GLM 5.3 and one
project. The fixture required lowercase values in `config.json`.

| Check | Result |
|---|---|
| Fetch the specification from the website | Pass |
| Save the specification and its version locally | Pass, with text differences |
| Find JSON and cite its approval | Pass |
| Write the approved value to the configuration | Fail, wrote `JSON` instead of `json` |
| Record the later XML approval and decision history | Pass |
| Write the updated value to the configuration | Fail, wrote `XML` instead of `xml` |

The setup agent used the model provider's `webReader` to fetch the website
and the plain-text specification. It saved a versioned local copy and linked
it from the project. The copy differed from the fetched text in blank lines,
one pair of quotation marks, and line wrapping. It was not byte-identical.

Fresh agents then identified Leo Park's JSON approval and updated the notes
after his later XML approval. Neither handoff log shows a network tool call.
The agents had instructions to use only project files. Shell and client web
tools were disabled. The operating system did not block network access, and
the provider can supply its own web tools. This is evidence of local use in
these runs, not a test under enforced network isolation.

The uppercase configuration values violate the fixture's README. The test
does not show whether OAK caused this error. The setup took 131 seconds and
12 client tool calls. The first handoff took 22 seconds and 6 calls. The XML
update took 39 seconds and 11 calls. These times describe single runs.

The logs and project are in `/tmp/oak-website-handoff-20261118/`. Temporary
storage can be cleared. No human edited the project during the agent runs.
