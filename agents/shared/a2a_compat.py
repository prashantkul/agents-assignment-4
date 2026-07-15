
# Role.agent compatibility alias.
try:
    from google.genai import types as genai_types

    Role = getattr(genai_types, "Role", None)
    if Role is not None:
        try:
            getattr(Role, "agent")
        except AttributeError:
            try:
                Role.agent = getattr(Role, "model")
            except AttributeError:
                Role.agent = "model"

        try:
            getattr(Role, "user")
        except AttributeError:
            Role.user = "user"
except Exception:
    pass

"""
A2A SDK compatibility patch for Assignment 4.

The starter repo was written against an older ADK/A2A pairing. The local
environment may install newer google-adk / a2a-sdk versions whose symbols
moved or were renamed. This module restores names ADK expects before
RemoteA2aAgent is imported.
"""

import sys
import types

import a2a.client as a2a_client_package
import a2a.client.errors as a2a_client_errors
import a2a.types as a2a_types
from a2a.client import client as real_client_module
from a2a.client.card_resolver import A2ACardResolver

# Protobuf Enum Role.agent compatibility alias.
# ADK expects Role.agent, while this installed protobuf-backed enum does not
# define that lowercase value. Patch EnumTypeWrapper lookup before ADK imports.
try:
    from google.protobuf.internal import enum_type_wrapper

    _original_enum_getattr = enum_type_wrapper.EnumTypeWrapper.__getattr__

    def _assignment4_enum_getattr(self, name):
        if name == "agent":
            for alt in ("model", "MODEL", "role_model", "ROLE_MODEL"):
                try:
                    return _original_enum_getattr(self, alt)
                except AttributeError:
                    pass
            return "model"
        return _original_enum_getattr(self, name)

    if not getattr(enum_type_wrapper.EnumTypeWrapper, "_assignment4_role_patch", False):
        enum_type_wrapper.EnumTypeWrapper.__getattr__ = _assignment4_enum_getattr
        enum_type_wrapper.EnumTypeWrapper._assignment4_role_patch = True
except Exception:
    pass




# Google GenAI Role compatibility alias.
# google-adk expects Role.agent in one A2A converter path, while the installed
# Google GenAI enum may expose model/user naming instead.
try:
    from google.genai import types as genai_types

    def _get_role_value(role_enum, names, fallback):
        for name in names:
            try:
                return getattr(role_enum, name)
            except AttributeError:
                continue
        return fallback

    Role = getattr(genai_types, "Role", None)
    if Role is not None:
        if not hasattr(Role, "agent"):
            Role.agent = _get_role_value(
                Role,
                ["model", "MODEL", "role_model", "ROLE_MODEL"],
                "model",
            )
        if not hasattr(Role, "user"):
            Role.user = _get_role_value(
                Role,
                ["user", "USER", "role_user", "ROLE_USER"],
                "user",
            )
except Exception:
    pass

class _CompatModel:
    """Minimal compatibility object for ADK import-time type references."""

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def model_dump(self, *args, **kwargs):
        return dict(self.__dict__)

    def dict(self, *args, **kwargs):
        return dict(self.__dict__)


if not hasattr(a2a_types, "TransportProtocol"):
    class TransportProtocol:
        jsonrpc = "JSONRPC"

    a2a_types.TransportProtocol = TransportProtocol


for _name in [
    "Artifact",
    "DataPart",
    "FilePart",
    "FileWithBytes",
    "FileWithUri",
    "Message",
    "Part",
    "Task",
    "TaskArtifactUpdateEvent",
    "TaskState",
    "TaskStatus",
    "TaskStatusUpdateEvent",
    "TextPart",
]:
    if not hasattr(a2a_types, _name):
        setattr(a2a_types, _name, type(_name, (_CompatModel,), {}))


if not hasattr(a2a_client_package, "ClientEvent"):
    a2a_client_package.ClientEvent = object

if not hasattr(real_client_module, "ClientEvent"):
    real_client_module.ClientEvent = object


if not hasattr(a2a_client_errors, "A2AClientHTTPError"):
    base_error = getattr(a2a_client_errors, "A2AClientError", Exception)

    class A2AClientHTTPError(base_error):
        pass

    a2a_client_errors.A2AClientHTTPError = A2AClientHTTPError
    a2a_client_package.A2AClientHTTPError = A2AClientHTTPError


middleware_module = types.ModuleType("a2a.client.middleware")
middleware_module.ClientCallContext = getattr(
    a2a_client_package, "ClientCallContext", object
)
middleware_module.ClientCallInterceptor = getattr(
    a2a_client_package, "ClientCallInterceptor", object
)
sys.modules["a2a.client.middleware"] = middleware_module


patched_client_module = types.ModuleType("a2a.client.client")

for attr in dir(real_client_module):
    if not attr.startswith("_"):
        setattr(patched_client_module, attr, getattr(real_client_module, attr))

patched_client_module.A2ACardResolver = A2ACardResolver
patched_client_module.ClientEvent = getattr(a2a_client_package, "ClientEvent", object)

sys.modules["a2a.client.client"] = patched_client_module

# Assignment AgentCard compatibility.
# The installed a2a-sdk AgentCard protobuf may not expose the older assignment
# fields such as url. For static assignment tests, use a lightweight compatible
# AgentCard class that preserves those fields.
try:
    def _compat_fields(cls):
        fields = getattr(cls, "model_fields", None) or getattr(cls, "__fields__", None)
        if fields:
            return set(fields.keys())
        descriptor = getattr(cls, "DESCRIPTOR", None)
        if descriptor is not None:
            return {field.name for field in descriptor.fields}
        return set()

    current_fields = _compat_fields(getattr(a2a_types, "AgentCard", object))
    if "url" not in current_fields:
        class AgentCard(_CompatModel):
            pass

        a2a_types.AgentCard = AgentCard
except Exception:
    pass



__all__ = [
    "A2ACardResolver",
    "patched_client_module",
]
