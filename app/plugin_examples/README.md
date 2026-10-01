# Declarative plugin examples

These manifests are bundled with the host and pinned by SHA-256 in `muse_plugin_sdk.py`. They declare an action the host already knows how to perform; they contain no Python entry point, shell command, downloaded package, credential, or dynamic import. A hash detects a changed manifest; it does not prove an outside author's identity.

`hello-capability.json` accepts `{"name":"Muse"}` and returns `{"message":"Hello, Muse!"}` from a reviewed host function. It requests no file, network, process, or secret access.

`browser-helper-1.0.json` and `browser-helper-1.1.json` delegate only to the existing `browser.research` Capability DSL for Python.org. Version 1.0 allows one page; 1.1 allows up to three. The host must supply the exact approved Goal call, domain scope, and GUI lease through `ApprovedActionBus`. The plugin cannot create approval or bypass that bus. This is the minimum integration pattern:

```python
from muse_plugin_sdk import DeclarativePluginSDK, PluginAwareExecutor
from muse_action_bus import ApprovedActionBus

sdk = DeclarativePluginSDK(workspace)
sdk.install("example.browser-helper", "1.1.0", approved=True)  # host records user approval
sdk.decide("example.browser-helper", "enable", approved=True)
executor = PluginAwareExecutor(capability_executor, sdk)
action_bus = ApprovedActionBus(workspace, executor)
```

The `approved=True` arguments above must come from the host's separate user approval records. Neither a model nor plugin input may set them. When browser-helper is disabled or revoked, `PluginAwareExecutor` delegates to the existing reviewed browser capability without the plugin. Upgrade disables the plugin until renewed approval. Unknown third-party code remains metadata-only in `PluginRegistry`; this SDK does not install or execute it.
